import pytest

from app.services.chat_language import (
    detect_language,
    extract_entities,
    normalize_text,
    route_intent,
)


@pytest.mark.parametrize(
    ("message", "language", "intent", "crop"),
    [
        ("mazhya kandyala javalpass kuthe changala dar milel", "mr", "best_mandi", "onion"),
        ("माझ्या कांद्याला जवळपास कुठे चांगला दर मिळेल?", "mr", "best_mandi", "onion"),
        ("आज टमाटर का सबसे अच्छा भाव किस मंडी में मिलेगा?", "hi", "best_mandi", "tomato"),
        ("mera pyaaz kahan bechun, 20 quintal hai", "hi", "best_mandi", "onion"),
        ("आता कांदा विकू का थांबू?", "mr", "sell_or_wait", "onion"),
        ("net profit म्हणजे काय?", "mr", "term_meaning", None),
        ("सोयाबीन की जगह इस बार क्या लगाऊं?", "hi", "which_crop", "soybean"),
        ("What is today's onion price?", "en", "price_today", "onion"),
        ("When does soybean price rise seasonally?", "en", "seasonality", "soybean"),
        ("How do I use the app?", "en", "app_help", None),
    ],
)
def test_golden_utterances(message, language, intent, crop):
    assert detect_language(message).language == language
    result = route_intent(message)
    assert result.intent == intent
    assert result.entities.crop == crop


@pytest.mark.parametrize(
    "message",
    [f"nearby mandi for {crop}" for crop in ("onion", "tomato", "soybean", "wheat", "jowar", "gram", "cotton", "pomegranate")]
    + [f"today price of {crop}" for crop in ("onion", "tomato", "soybean", "wheat", "jowar", "gram", "cotton", "pomegranate")]
    + [f"should I sell {crop} now?" for crop in ("onion", "tomato", "soybean", "wheat", "jowar", "gram", "cotton", "pomegranate")]
    + [f"what crop should I grow after {crop}?" for crop in ("onion", "tomato", "soybean", "wheat", "jowar", "gram", "cotton", "pomegranate")]
    + [
        f"{number} kg {crop} rate"
        for number in (10, 20, 50, 100, 250, 500, 1000, 2000)
        for crop in ("onion", "tomato")
    ],
)
def test_additional_utterances_route_without_errors(message):
    result = route_intent(message)
    assert result.intent != "unknown"


def test_units_convert_to_quintals():
    assert extract_entities("100 kg onion").quantity_quintal == pytest.approx(1)
    assert extract_entities("2 ton wheat").quantity_quintal == pytest.approx(20)
    assert extract_entities("20 quintal pyaaz").quantity_quintal == pytest.approx(20)


def test_normalization_keeps_devanagari_and_collapses_spacing():
    assert normalize_text("  कांदा!!!   भाव? ") == "कांदा भाव"


def test_out_of_scope_and_distress_have_priority():
    assert route_intent("which pesticide dose should I use?").intent == "out_of_scope"
    assert route_intent("I want to die, tell me the mandi price").intent == "distress"
