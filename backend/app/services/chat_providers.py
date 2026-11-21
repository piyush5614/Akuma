from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Protocol


class ProviderUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class ProviderResult:
    text: str | None = None
    tool_calls: list[dict[str, Any]] = field(default_factory=list)


class ChatLLMProvider(Protocol):
    def complete(self, messages: list[dict[str, str]], tools: list[dict[str, Any]]) -> ProviderResult:
        ...


class RulesProvider:
    """Rules mode provider; it never calls a network or an LLM."""

    def complete(self, messages: list[dict[str, str]], tools: list[dict[str, Any]]) -> ProviderResult:
        return ProviderResult()


class _JsonHTTPProvider:
    def __init__(self, api_key: str | None, model: str, endpoint: str, timeout_seconds: float = 8):
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def _post(self, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        if not self.api_key:
            raise ProviderUnavailable("LLM provider is not configured")
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", **headers},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise ProviderUnavailable("LLM provider request failed") from exc


class OpenAICompatibleProvider(_JsonHTTPProvider):
    def complete(self, messages: list[dict[str, str]], tools: list[dict[str, Any]]) -> ProviderResult:
        payload = {"model": self.model, "messages": messages, "tools": tools}
        body = self._post(payload, {"Authorization": f"Bearer {self.api_key}"})
        choice = body.get("choices", [{}])[0].get("message", {})
        calls = [
            {"name": call.get("function", {}).get("name"), "arguments": call.get("function", {}).get("arguments", "{}")}
            for call in choice.get("tool_calls", [])
        ]
        return ProviderResult(text=choice.get("content"), tool_calls=calls)


class AnthropicProvider(_JsonHTTPProvider):
    def complete(self, messages: list[dict[str, str]], tools: list[dict[str, Any]]) -> ProviderResult:
        system = next((message["content"] for message in messages if message["role"] == "system"), "")
        user_messages = [message for message in messages if message["role"] != "system"]
        payload = {"model": self.model, "max_tokens": 512, "system": system, "messages": user_messages, "tools": tools}
        body = self._post(payload, {"x-api-key": self.api_key or "", "anthropic-version": "2023-06-01"})
        blocks = body.get("content", [])
        text = "".join(block.get("text", "") for block in blocks if block.get("type") == "text") or None
        calls = [
            {"name": block.get("name"), "arguments": block.get("input", {})}
            for block in blocks
            if block.get("type") == "tool_use"
        ]
        return ProviderResult(text=text, tool_calls=calls)


def configured_provider() -> ChatLLMProvider:
    mode = os.getenv("CHAT_PROVIDER", "rules").lower()
    model = os.getenv("CHAT_MODEL", "")
    if mode == "anthropic":
        return AnthropicProvider(os.getenv("ANTHROPIC_API_KEY"), model, os.getenv("ANTHROPIC_URL", "https://api.anthropic.com/v1/messages"))
    if mode in {"openai", "openai-compatible"}:
        return OpenAICompatibleProvider(os.getenv("OPENAI_API_KEY"), model, os.getenv("OPENAI_URL", "https://api.openai.com/v1/chat/completions"))
    return RulesProvider()
