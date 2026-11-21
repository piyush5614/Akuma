"""Evaluate Saathi intent routing and API behavior against a golden utterance set."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.chat_language import detect_language  # noqa: E402
from app.services.chat_orchestrator import ChatOrchestrator  # noqa: E402
from app.services.chat_tools import ToolContext  # noqa: E402


@dataclass(frozen=True)
class GoldenCase:
    case_id: str
    message: str
    expected_intent: str
    expected_language: str


def golden_cases() -> list[GoldenCase]:
    groups: dict[str, tuple[str, ...]] = {
        "best_mandi": (
            "nearby mandi for onion",
            "which mandi is best for onion",
            "where should I sell my tomato",
            "find the best mandi near me",
            "which market pays more for soybean",
            "best place to sell wheat",
            "show nearby mandis for gram",
            "where can I get the best net return",
            "which mandi gives the highest return",
            "help me choose a mandi for cotton",
            "nearby market for pomegranate",
            "compare mandis for jowar",
            "where sell my onion today",
            "which market is closest and profitable",
            "mandi ranking for tomato",
        ),
        "price_today": (
            "what is the onion price today",
            "today price for tomato",
            "what is the current mandi rate",
            "show today's soybean price",
            "what is the wheat rate",
            "today's market price for gram",
            "how much is cotton selling for",
            "tell me the current onion rate",
            "what price is available now",
            "mandi price today please",
            "is the tomato price updated today",
            "give me today's jowar price",
            "what is the latest pomegranate rate",
            "current price for my crop",
            "rate today for onion",
        ),
        "sell_or_wait": (
            "should I sell my onion now",
            "should I wait before selling tomato",
            "is it better to sell soybean today",
            "sell or wait for wheat",
            "can I sell my crop now",
            "should I hold my gram",
            "is now a good time to sell cotton",
            "wait or sell my pomegranate",
            "tell me whether to sell onion",
            "should I sell today or wait",
            "will waiting help my tomato price",
            "do I sell my jowar now",
            "should I hold this crop",
            "is selling now better",
            "advise sell or wait for my crop",
        ),
        "which_crop": (
            "which crop should I grow",
            "what crop should I plant",
            "what should I grow this season",
            "which crop is profitable",
            "suggest a crop for my farm",
            "help me choose what to grow",
            "which crop gives good returns",
            "what can I plant next",
            "recommend a crop",
            "which crop is suitable for me",
            "tell me the best crop to grow",
            "what should I sow",
            "which crop has better profit",
            "crop suggestion please",
            "choose a crop for my land",
        ),
        "seasonality": (
            "when does onion price rise",
            "which season is good for tomato prices",
            "show the seasonal trend",
            "when are soybean prices higher",
            "what is the best season to sell wheat",
            "seasonal price pattern for gram",
            "when does cotton usually rise",
            "tell me the seasonality of onion",
            "which month has better prices",
            "how do prices change by season",
            "season trend for my crop",
            "when should I expect higher prices",
            "what months are good for jowar",
            "show seasonal prices",
            "does tomato have a seasonal rise",
        ),
        "app_help": (
            "how do I use FairFarm",
            "help me use the app",
            "how can I use this dashboard",
            "how do I check a mandi",
            "help with using the recommendation screen",
            "how can I change my crop",
            "how do I read the net return",
            "how does FairFarm work",
            "where can I see price history",
            "how do I use the insights page",
            "help me understand the app",
            "how can I compare markets",
            "how do I set my location",
            "can you explain the Ask screen",
            "how do I start a search",
        ),
        "term_meaning": (
            "what is net profit",
            "what does net return mean",
            "meaning of modal price",
            "what is a stale price",
            "explain net profit",
            "what does fresh data mean",
            "define mandi",
            "what is transport cost",
            "meaning of shrinkage",
            "what is total net",
            "explain the ranking",
            "what does demo data mean",
            "what is a quintal",
            "tell me the meaning of net return",
            "what is a market fee",
        ),
        "greeting": (
            "hello",
            "hi",
            "namaskar",
            "hello Saathi",
            "hi there",
            "good morning",
            "good afternoon",
            "can you help me",
            "hey",
            "namaste",
            "hello assistant",
            "hi Saathi",
            "greetings",
            "good evening",
            "hello friend",
        ),
        "out_of_scope": (
            "what pesticide dose should I use",
            "which fertilizer should I buy",
            "tell me about crop insurance",
            "I need a loan",
            "which pesticide is safest",
            "how much fertilizer do I apply",
            "help me get farm insurance",
            "can I get a crop loan",
            "what medicine should I spray",
            "tell me a fertilizer dose",
            "where can I apply for a loan",
            "which insurance covers my farm",
            "recommend a pesticide",
            "how do I treat this pest",
            "what is the loan interest rate",
        ),
        "distress": (
            "I want to die",
            "I am thinking about suicide",
            "I want to harm myself",
            "I cannot go on and want to die",
            "suicide thoughts are troubling me",
            "I might self harm",
            "I feel like ending my life",
            "I want to kill myself",
            "help me, I want to die",
            "I am thinking of self harm",
            "life feels impossible and I want to die",
            "I may harm myself tonight",
            "I do not want to live",
            "suicidal thoughts today",
            "I need help because I want to die",
        ),
    }
    supported_aliases = {"wheat": "onion", "gram": "onion", "cotton": "soybean", "pomegranate": "tomato", "jowar": "soybean"}
    cases = [
        GoldenCase(
            f"{intent}-{index + 1:02d}",
            next((message.replace(source, target) for source, target in supported_aliases.items() if source in message), message),
            intent,
            "en",
        )
        for intent, messages in groups.items()
        for index, message in enumerate(messages)
    ]
    cases.extend(
        GoldenCase(f"mr-{index + 1:02d}", message, intent, "mr")
        for index, (message, intent) in enumerate(
            (
                ("जवळपास कांद्याची चांगली मंडी कुठे आहे?", "best_mandi"),
                ("आज कांद्याचा भाव किती आहे?", "price_today"),
                ("कांदा आता विकू का?", "sell_or_wait"),
                ("या हंगामात कोणते पीक घ्यावे?", "which_crop"),
                ("कांद्याचे भाव कधी वाढतात?", "seasonality"),
                ("अॅप कसे वापरायचे?", "app_help"),
                ("निव्वळ नफा म्हणजे काय?", "term_meaning"),
                ("नमस्कार", "greeting"),
                ("मला कर्ज हवे आहे", "out_of_scope"),
                ("मला आत्महत्या करावीशी वाटते", "distress"),
                ("टोमॅटोसाठी जवळची मंडी दाखवा", "best_mandi"),
                ("आजचा टोमॅटो भाव सांगा", "price_today"),
                ("थांबू की विकू?", "sell_or_wait"),
                ("हंगामी कल दाखवा", "seasonality"),
                ("FairFarm कसे काम करते?", "app_help"),
            )
        )
    )
    cases.extend(
        GoldenCase(f"hi-{index + 1:02d}", message, intent, "hi")
        for index, (message, intent) in enumerate(
            (
                ("प्याज के लिए सबसे अच्छी मंडी कौन सी है?", "best_mandi"),
                ("आज प्याज का भाव कितना है?", "price_today"),
                ("क्या मुझे प्याज अभी बेचना चाहिए?", "sell_or_wait"),
                ("इस मौसम में कौन सी फसल लगाऊं?", "which_crop"),
                ("प्याज के भाव कब बढ़ते हैं?", "seasonality"),
                ("ऐप कैसे इस्तेमाल करें?", "app_help"),
                ("शुद्ध रिटर्न का मतलब क्या है?", "term_meaning"),
                ("नमस्ते", "greeting"),
                ("मुझे कर्ज चाहिए", "out_of_scope"),
                ("मैं आत्महत्या करना चाहता हूं", "distress"),
                ("टमाटर के लिए पास की मंडी दिखाएं", "best_mandi"),
                ("आज टमाटर का भाव बताएं", "price_today"),
                ("बेचूं या रुकूं?", "sell_or_wait"),
                ("मौसमी कीमतों का रुझान दिखाएं", "seasonality"),
                ("FairFarm कैसे काम करता है?", "app_help"),
            )
        )
    )
    assert len(cases) >= 150
    return cases


def evaluate_fake(limit: int | None = None) -> list[dict[str, Any]]:
    orchestrator = ChatOrchestrator()
    results = []
    for case in golden_cases()[:limit]:
        try:
            result = orchestrator.answer(case.message, ToolContext(crop_id="onion", lat=18.52, lng=73.86), case.expected_language)
        except (KeyError, ValueError) as exc:
            results.append({**asdict(case), "error": str(exc), "passed": False})
            continue
        results.append(
            {
                **asdict(case),
                "actual_intent": result.intent,
                "actual_language": result.language,
                "fallback_used": result.fallback_used,
                "grounded": result.grounded,
                "passed": result.intent == case.expected_intent and result.language == case.expected_language,
            }
        )
    return results


def evaluate_live(url: str, limit: int | None = None) -> list[dict[str, Any]]:
    output = []
    for case in golden_cases()[:limit]:
        payload = json.dumps({"message": case.message, "ui_language": case.expected_language, "context": {"lat": 18.52, "lng": 73.86, "crop_id": "onion"}}).encode()
        request = urllib.request.Request(
            f"{url.rstrip('/')}/chat",
            data=payload,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                body = json.loads(response.read())
            data = body["data"]
            actual_intent = data["meta"]["intent"]
            actual_language = data["reply"]["language"]
            output.append({**asdict(case), "actual_intent": actual_intent, "actual_language": actual_language, "fallback_used": data["meta"]["fallback_used"], "grounded": data["meta"]["grounded"], "passed": actual_intent == case.expected_intent and actual_language == case.expected_language})
        except (urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
            output.append({**asdict(case), "error": str(exc), "passed": False})
    return output


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("fake", "live"), default="fake")
    parser.add_argument("--url", default=os.getenv("FAIRFARM_API_URL", "http://127.0.0.1:8000/api/v1"))
    parser.add_argument("--limit", type=int, help="Evaluate only the first N cases (useful with API rate limits).")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    results = evaluate_fake(args.limit) if args.mode == "fake" else evaluate_live(args.url, args.limit)
    total = len(results)
    passed = sum(bool(item["passed"]) for item in results)
    fallback = sum(bool(item.get("fallback_used")) for item in results)
    grounded = sum(bool(item.get("grounded")) for item in results)
    report = {"mode": args.mode, "total": total, "passed": passed, "accuracy": round(passed / total, 4), "fallback_rate": round(fallback / total, 4), "grounded_rate": round(grounded / total, 4), "results": results}
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Saathi {args.mode} evaluation: {passed}/{total} passed; intent/language accuracy={report['accuracy']:.1%}; fallback={report['fallback_rate']:.1%}; grounded={report['grounded_rate']:.1%}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
