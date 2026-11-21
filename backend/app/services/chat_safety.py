from __future__ import annotations

import re
from dataclasses import dataclass

from .chat_language import route_intent

_PHONE = re.compile(r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{9}(?!\d)")
_AADHAAR = re.compile(r"(?<!\d)\d{4}[\s-]?\d{4}[\s-]?\d{4}(?!\d)")
_BANK = re.compile(r"(?i)\b(?:account|a\/c|ifsc|bank)\b[\w\s:/-]{0,30}\d{6,}")
_INJECTION = ("ignore previous", "reveal prompt", "system prompt", "change your rules")


@dataclass(frozen=True)
class SafetyResult:
    allowed: bool
    category: str | None = None
    message_key: str | None = None


def check_safety(message: str) -> SafetyResult:
    lowered = message.lower()
    if any(term in lowered for term in _INJECTION):
        return SafetyResult(False, "prompt_injection", "out_of_scope")
    routed = route_intent(message)
    if routed.intent == "distress":
        return SafetyResult(False, "distress", "distress")
    if routed.intent == "out_of_scope":
        return SafetyResult(False, "out_of_scope", "out_of_scope")
    return SafetyResult(True)


def redact_sensitive(text: str) -> str:
    redacted = _PHONE.sub("[REDACTED_PHONE]", text)
    redacted = _AADHAAR.sub("[REDACTED_ID]", redacted)
    return _BANK.sub("[REDACTED_BANK]", redacted)
