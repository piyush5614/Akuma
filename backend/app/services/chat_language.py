from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import yaml

_GLOSSARY_PATH = Path(__file__).resolve().parents[1] / "i18n" / "glossary.yaml"
_DEVANAGARI = re.compile(r"[\u0900-\u097f]")
_NUMBER = re.compile(r"(?<!\w)(\d+(?:[.,]\d+)?)\s*([a-zA-Z\u0900-\u097f]*)")
_PUNCTUATION = re.compile(r"[^\w\s\u0900-\u097f]", re.UNICODE)


@dataclass(frozen=True)
class GlossaryEntry:
    canonical: str
    aliases: tuple[str, ...]
    conversion_to_quintal: float | None = None


@dataclass(frozen=True)
class ExtractedEntities:
    crop: str | None = None
    quantity_quintal: float | None = None
    source_unit: str | None = None
    market_terms: tuple[str, ...] = ()
    time_terms: tuple[str, ...] = ()


@dataclass(frozen=True)
class LanguageResult:
    language: str
    script: str
    confidence: float


@dataclass(frozen=True)
class IntentResult:
    intent: str
    confidence: float
    entities: ExtractedEntities = field(default_factory=ExtractedEntities)


def normalize_text(message: str) -> str:
    """Normalize user text without transliterating or changing its language."""
    normalized = unicodedata.normalize("NFC", message).strip().lower()
    normalized = normalized.replace("’", "'").replace("०", "0").replace("१", "1")
    normalized = _PUNCTUATION.sub(" ", normalized)
    return " ".join(normalized.split())


def _load_glossary() -> tuple[GlossaryEntry, ...]:
    raw: dict[str, Any] = yaml.safe_load(_GLOSSARY_PATH.read_text(encoding="utf-8"))
    return tuple(
        GlossaryEntry(
            canonical=item["canonical"],
            aliases=tuple(normalize_text(alias) for alias in item["aliases"]),
            conversion_to_quintal=item.get("conversion_to_quintal"),
        )
        for item in raw["entries"]
    )


GLOSSARY = _load_glossary()
_CROP_IDS = {
    "onion", "tomato", "potato", "cabbage", "cauliflower", "okra", "brinjal",
    "green_chilli", "wheat", "rice", "maize", "soybean", "jowar", "gram",
    "cotton", "turmeric", "groundnut", "sunflower", "sugarcane", "barley",
    "banana", "mango", "pomegranate", "grapes", "orange",
}
_CROPS = {entry.canonical: entry for entry in GLOSSARY if entry.canonical in _CROP_IDS}
_UNITS = {entry.canonical: entry for entry in GLOSSARY if entry.conversion_to_quintal is not None}
_MARKET_CANONICALS = {"market_rate", "market", "nearby"}
_MARATHI_MARKERS = {"mazha", "mazhya", "kandyala", "kuthe", "changala", "vik", "thambu", "pike", "javalpass"}
_HINDI_MARKERS = {"mera", "meri", "kahan", "kaise", "bechun", "sabse", "achha", "fasal"}
_MARATHI_DEVANAGARI = {"कांदा", "कांद्याला", "टोमॅटो", "ज्वारी", "गहू", "कुठे", "जवळपास", "आता", "म्हणजे"}
_HINDI_DEVANAGARI = {"प्याज", "टमाटर", "चना", "कहाँ", "कैसे", "फसल", "बेचूं", "सबसे"}


def detect_language(message: str) -> LanguageResult:
    normalized = normalize_text(message)
    devanagari_tokens = set(_DEVANAGARI.findall(normalized))
    del devanagari_tokens
    tokens = set(normalized.split())
    marathi_score = len(tokens & _MARATHI_MARKERS) + sum(token in normalized for token in _MARATHI_DEVANAGARI)
    hindi_score = len(tokens & _HINDI_MARKERS) + sum(token in normalized for token in _HINDI_DEVANAGARI)
    devanagari_count = len(_DEVANAGARI.findall(normalized))
    latin_count = sum(character.isascii() and character.isalpha() for character in normalized)
    script = "devanagari" if devanagari_count > latin_count else "latin"
    if marathi_score == hindi_score == 0:
        language = "en" if latin_count else "hi"
        confidence = 0.55
    elif marathi_score >= hindi_score:
        language = "mr"
        confidence = min(0.99, 0.65 + marathi_score * 0.08)
    else:
        language = "hi"
        confidence = min(0.99, 0.65 + hindi_score * 0.08)
    return LanguageResult(language=language, script=script, confidence=confidence)


def _alias_match(text: str, entry: GlossaryEntry) -> bool:
    if any(re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", text) for alias in entry.aliases):
        return True
    for token in text.split():
        if len(token) >= 4 and any(SequenceMatcher(None, token, alias).ratio() >= 0.86 for alias in entry.aliases):
            return True
    return False


def extract_entities(message: str) -> ExtractedEntities:
    normalized = normalize_text(message)
    crop = next((entry.canonical for entry in _CROPS.values() if _alias_match(normalized, entry)), None)
    market_terms = tuple(entry.canonical for entry in GLOSSARY if entry.canonical in _MARKET_CANONICALS and _alias_match(normalized, entry))
    time_terms = tuple(term for term in ("today", "aaj", "आज", "now", "आता") if term in normalized)
    quantity_quintal = None
    source_unit = None
    for match in _NUMBER.finditer(normalized):
        number = float(match.group(1).replace(",", ""))
        raw_unit = match.group(2).strip()
        unit = next((entry for entry in _UNITS.values() if raw_unit in entry.aliases), None)
        if unit is None and raw_unit:
            unit = next((entry for entry in _UNITS.values() if _alias_match(raw_unit, entry)), None)
        if unit is not None:
            quantity_quintal = number * float(unit.conversion_to_quintal or 1)
            source_unit = unit.canonical
            break
        if quantity_quintal is None:
            quantity_quintal = number
            source_unit = "quintal"
    return ExtractedEntities(
        crop=crop,
        quantity_quintal=quantity_quintal,
        source_unit=source_unit,
        market_terms=market_terms,
        time_terms=time_terms,
    )


_INTENT_TERMS: dict[str, tuple[str, ...]] = {
    "distress": ("suicide", "suicidal", "self harm", "harm myself", "want to die", "ending my life", "kill myself", "do not want to live", "मरना", "आत्महत्या", "जीव द्यावा"),
    "out_of_scope": ("pesticide", "fertilizer", "medicine", "spray", "pest", "दवा", "कीटनाशक", "कर्ज", "loan", "insurance"),
    "greeting": ("hello", "hi", "namaskar", "namaste", "hey", "greetings", "good morning", "good afternoon", "good evening", "नमस्कार", "नमस्ते"),
    "app_help": ("how to use", "how do i use", "help me use", "how does fairfarm work", "how can i", "where can i", "help with", "check a mandi", "read the net return", "understand the app", "set my location", "start a search", "can you explain the ask", "कसे वापर", "कसे काम", "कैसे इस्तेमाल", "कैसे काम", "offline"),
    "sell_or_wait": ("sell now", "should i sell", "sell or wait", "wait before", "wait or sell", "hold", "is selling now", "better to sell", "can i sell", "time to sell", "whether to sell", "do i sell", "waiting help", "विकू", "विकू का", "बेचूं", "थांबू"),
    "which_crop": ("which crop", "what crop", "what to grow", "what should i", "what can i plant", "suggest a crop", "recommend a crop", "crop suggestion", "best crop", "choose a crop", "पीक", "फसल", "लगाऊं"),
    "seasonality": ("season", "seasonal", "seasonality", "price rise", "prices rise", "higher prices", "prices higher", "usually rise", "which month", "what months", "हंगाम", "मौसम", "कधी वाढ"),
    "trend": ("price trend", "trend", "last 7 days", "past week", "weekly trend", "month trend", "past 30 days", "कल किती", "भाव कल"),
    "arrivals": ("arrival", "arrivals", "arrival report", "how much supply", "supply", "टक्का", "आवक"),
    "best_mandi": (
        "best mandi", "which mandi", "nearby mandi", "nearby mandis", "nearby market", "where sell", "where should i sell", "where can i get", "which market", "best place to sell",
        "help me choose a mandi", "compare mandis", "mandi ranking", "highest return", "best net return", "kahan", "bechun", "मंडी", "मंडीत",
        "जवळपास", "कुठे", "javalpass",
    ),
    "price_today": ("today price", "current price", "today", "price", "rate", "आजचा भाव", "आज भाव", "आज का भाव", "भाव"),
    "term_meaning": ("meaning", "what does", "define", "explain", "what is net profit", "what is modal price", "what is stale price", "what is fresh data", "what is transport cost", "what is total net", "what is a quintal", "what is a market fee", "म्हणजे काय", "निव्वळ नफा", "मतलब क्या", "शुद्ध रिटर्न", "net profit"),
}


def _contains_term(normalized: str, term: str) -> bool:
    return bool(re.search(rf"(?<!\w){re.escape(term)}(?!\w)", normalized))


def route_intent(message: str) -> IntentResult:
    normalized = normalize_text(message)
    entities = extract_entities(normalized)
    if any(_contains_term(normalized, term) for term in _INTENT_TERMS["app_help"]):
        return IntentResult(intent="app_help", confidence=0.9, entities=entities)
    if any(_contains_term(normalized, term) for term in _INTENT_TERMS["term_meaning"]):
        return IntentResult(intent="term_meaning", confidence=0.9, entities=entities)
    for intent, terms in _INTENT_TERMS.items():
        if intent == "term_meaning":
            continue
        if any(_contains_term(normalized, term) for term in terms):
            return IntentResult(intent=intent, confidence=0.9, entities=entities)
    return IntentResult(intent="unknown", confidence=0.35, entities=entities)
