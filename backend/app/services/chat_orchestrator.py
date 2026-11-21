from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass
from typing import Any

from .chat_language import IntentResult, detect_language, route_intent
from .chat_providers import ChatLLMProvider, ProviderResult, ProviderUnavailable, RulesProvider
from .chat_safety import SafetyResult, check_safety, redact_sensitive
from .chat_tools import ToolContext, ToolRegistry


@dataclass(frozen=True)
class OrchestrationResult:
    text: str
    language: str
    script: str
    intent: str
    tools_used: tuple[str, ...]
    grounded: bool
    fallback_used: bool
    is_demo: bool = True
    tool_results: tuple[dict[str, Any], ...] = ()


class TTLCache:
    def __init__(self, ttl_seconds: int = 600):
        self.ttl_seconds = ttl_seconds
        self._items: dict[str, tuple[float, dict[str, Any]]] = {}

    def get(self, key: str) -> dict[str, Any] | None:
        item = self._items.get(key)
        if item and time.monotonic() - item[0] < self.ttl_seconds:
            return item[1]
        self._items.pop(key, None)
        return None

    def put(self, key: str, value: dict[str, Any]) -> None:
        self._items[key] = (time.monotonic(), value)


class GroundingValidator:
    def validate(self, text: str, tool_results: list[dict[str, Any]]) -> bool:
        factual_values = set()
        for result in tool_results:
            self._collect_strings(result, factual_values)
        numbers = {token for token in text.replace("₹", " ").replace(",", " ").split() if any(character.isdigit() for character in token)}
        return not numbers or all(number in " ".join(factual_values) for number in numbers)

    def _collect_strings(self, value: Any, output: set[str]) -> None:
        if isinstance(value, dict):
            for item in value.values():
                self._collect_strings(item, output)
        elif isinstance(value, list):
            for item in value:
                self._collect_strings(item, output)
        elif value is not None:
            output.add(str(value))


class ChatOrchestrator:
    def __init__(self, tools: ToolRegistry | None = None, provider: ChatLLMProvider | None = None, timeout_seconds: float = 8):
        self.tools = tools or ToolRegistry()
        self.provider = provider or RulesProvider()
        self.timeout_seconds = timeout_seconds
        self.cache = TTLCache()
        self.grounding = GroundingValidator()

    def answer(self, message: str, context: ToolContext | None = None, language: str = "auto") -> OrchestrationResult:
        detected = detect_language(message)
        output_language = detected.language if language == "auto" else language
        safety = check_safety(message)
        intent = route_intent(message)
        if not safety.allowed:
            return OrchestrationResult(self._safety_text(safety, output_language), output_language, "devanagari" if output_language != "en" else "latin", intent.intent, (), True, True)
        context = context or ToolContext()
        if isinstance(self.provider, RulesProvider):
            return self._rules_answer(message, intent, output_language, context)
        return self._provider_answer(message, intent, output_language, context)

    def _rules_answer(self, message: str, intent: IntentResult, language: str, context: ToolContext) -> OrchestrationResult:
        tool_name, args = self._tool_request(intent, message, context)
        if tool_name is None:
            return OrchestrationResult(self._fallback_text(language), language, "devanagari" if language != "en" else "latin", intent.intent, (), True, False)
        key = json.dumps([tool_name, args, context.model_dump(mode="json")], sort_keys=True, default=str) + language
        result = self.cache.get(key)
        if result is None:
            result = self.tools.invoke(tool_name, args, context)
            self.cache.put(key, result)
        text = self._template(intent.intent, result, language)
        grounded = self.grounding.validate(text, [result])
        if not grounded:
            text = self._fallback_text(language)
        return OrchestrationResult(text, language, "devanagari" if language != "en" else "latin", intent.intent, (tool_name,), grounded, not grounded, tool_results=(result,))

    def _provider_answer(self, message: str, intent: IntentResult, language: str, context: ToolContext) -> OrchestrationResult:
        messages = [{"role": "system", "content": "Use only validated FairFarm tools for factual claims."}, {"role": "user", "content": message}]
        tool_results: list[dict[str, Any]] = []
        text = None
        used: list[str] = []
        try:
            for _ in range(3):
                result = self._complete_with_timeout(messages)
                text = result.text or text
                if not result.tool_calls:
                    break
                for call in result.tool_calls:
                    name = call["name"]
                    arguments = call["arguments"]
                    if isinstance(arguments, str):
                        arguments = json.loads(arguments)
                    tool_result = self.tools.invoke(name, arguments, context)
                    tool_results.append(tool_result)
                    used.append(name)
                    messages.append({"role": "tool", "content": json.dumps(tool_result)})
            if not text or not self.grounding.validate(text, tool_results):
                return OrchestrationResult(self._fallback_text(language), language, "devanagari" if language != "en" else "latin", intent.intent, tuple(used), False, True, tool_results=tuple(tool_results))
            return OrchestrationResult(text, language, "devanagari" if language != "en" else "latin", intent.intent, tuple(used), True, False, tool_results=tuple(tool_results))
        except (ProviderUnavailable, ValueError, json.JSONDecodeError):
            return OrchestrationResult(self._fallback_text(language), language, "devanagari" if language != "en" else "latin", intent.intent, tuple(used), False, True, tool_results=tuple(tool_results))

    def _complete_with_timeout(self, messages: list[dict[str, str]]) -> ProviderResult:
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self.provider.complete, messages, self.tools.definitions_for_provider())
        try:
            return future.result(timeout=self.timeout_seconds)
        except TimeoutError as exc:
            future.cancel()
            raise ProviderUnavailable("LLM provider timed out") from exc
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    def _tool_request(self, intent: IntentResult, message: str, context: ToolContext) -> tuple[str | None, dict[str, Any]]:
        crop = intent.entities.crop or context.crop_id
        if intent.intent == "best_mandi" and crop:
            return "find_best_mandis", {"crop": crop, "quantity_quintal": intent.entities.quantity_quintal or context.quantity_quintal or 1}
        if intent.intent == "price_today" and crop and context.crop_id:
            return "get_mandi_price", {"crop": crop, "mandi": "pune"}
        if intent.intent == "sell_or_wait" and crop:
            return "get_sell_or_wait", {"crop": crop}
        if intent.intent == "seasonality" and crop:
            return "get_seasonality", {"crop": crop}
        if intent.intent == "which_crop":
            return "get_crop_suggestions", {}
        if intent.intent in {"term_meaning", "app_help"}:
            return ("explain_term" if intent.intent == "term_meaning" else "app_help"), {"term": message}
        return None, {}

    def _template(self, intent: str, result: dict[str, Any], language: str) -> str:
        if intent == "best_mandi":
            first = result.get("recommendations", [{}])[0]
            return f"{first.get('name', 'No mandi')} has the best estimated net return, ₹{first.get('costs', {}).get('net_per_quintal_inr', '0')} per quintal. Data is {first.get('freshness', 'unknown')}."
        if intent == "sell_or_wait":
            reason = result.get("reason", {})
            if hasattr(reason, "model_dump"):
                reason = reason.model_dump()
            return f"{reason.get(language, result.get('disclaimer', 'Guidance, not a guarantee'))} Guidance, not a guarantee."
        if intent in {"term_meaning", "app_help"}:
            return result.get("text") or self._fallback_text(language)
        return self._fallback_text(language)

    def _fallback_text(self, language: str) -> str:
        return {"en": "I can help with mandi prices, net returns, trends, and FairFarm features.", "mr": "मी मंडीचे भाव, निव्वळ परतावा, कल आणि FairFarm सुविधांमध्ये मदत करू शकतो.", "hi": "मैं मंडी भाव, शुद्ध रिटर्न, रुझान और FairFarm सुविधाओं में मदद कर सकता हूँ।"}[language]

    def _safety_text(self, safety: SafetyResult, language: str) -> str:
        if safety.category == "distress":
            return {"en": "I am sorry you are feeling this way. Please contact local emergency support or a trusted person. I cannot give market advice in this reply.", "mr": "तुम्हाला असे वाटत आहे याचे मला वाईट वाटते. कृपया स्थानिक आपत्कालीन मदत किंवा विश्वासू व्यक्तीशी संपर्क करा. या उत्तरात मी बाजाराचा सल्ला देऊ शकत नाही.", "hi": "आप ऐसा महसूस कर रहे हैं, इसका मुझे अफसोस है। कृपया स्थानीय आपात सहायता या किसी भरोसेमंद व्यक्ति से संपर्क करें। इस जवाब में मैं बाजार सलाह नहीं दे सकता।"}[language]
        return self._fallback_text(language)

    @staticmethod
    def redact_for_log(message: str) -> str:
        return redact_sensitive(message)
