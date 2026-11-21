from abc import ABC, abstractmethod
from typing import ClassVar

from ..schemas.common import LocalizedText


class ChatProvider(ABC):
    @abstractmethod
    def answer(self, message: str, language: str) -> dict:
        raise NotImplementedError


class RuleBasedChatProvider(ChatProvider):
    intents: ClassVar[dict[str, list[str]]] = {
        "best_mandi": ["mandi", "best", "बाजार", "मंडी"],
        "price_today": ["price", "भाव", "कीमत"],
        "sell_or_wait": ["sell", "wait", "विक", "बेच"],
        "which_crop": ["crop", "पीक", "फसल"],
    }

    def answer(self, message: str, language: str) -> dict:
        lowered = message.lower()
        intent = next((name for name, words in self.intents.items() if any(word in lowered for word in words)), "help")
        text = {
            "en": "I can compare net mandi returns, prices, selling guidance, and crop profit.",
            "mr": "मी मंडीचा निव्वळ परतावा, भाव, विक्री मार्गदर्शन आणि पीक नफा तुलना करू शकतो.",
            "hi": "मैं मंडी का शुद्ध रिटर्न, भाव, बिक्री मार्गदर्शन और फसल लाभ की तुलना कर सकता हूँ।",
        }
        return {"intent": intent, "answer": LocalizedText(**text), "suggestion_chips": ["Show prices", "Should I sell now?"]}
