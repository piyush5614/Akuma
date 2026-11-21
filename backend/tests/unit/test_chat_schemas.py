import pytest
from pydantic import ValidationError

from app.schemas.chat import (
    MandiRankingCard,
    SaathiChatRequest,
    SaathiChatResponse,
)


def test_saathi_request_accepts_context_and_client():
    request = SaathiChatRequest.model_validate(
        {
            "message": "mazhya kandyala javalpass kuthe changala dar milel",
            "ui_language": "auto",
            "context": {"lat": 18.52, "lng": 73.86, "crop_id": "onion"},
            "client": {"platform": "android", "app_version": "1.0.0"},
        }
    )

    assert request.context.crop_id == "onion"
    assert request.client.platform == "android"


def test_saathi_request_rejects_long_messages():
    with pytest.raises(ValidationError):
        SaathiChatRequest(message="x" * 501)


def test_response_validates_discriminated_card():
    response = SaathiChatResponse.model_validate(
        {
            "session_id": "session-1",
            "reply": {
                "text": "Pune gives the best return.",
                "speak_text": "Pune gives the best return.",
                "language": "en",
                "script": "latin",
            },
            "cards": [{"type": "mandi_ranking", "data": {"is_demo": True}}],
            "meta": {
                "intent": "best_mandi",
                "is_demo": True,
                "confidence": 0.9,
                "grounded": True,
                "fallback_used": False,
                "request_id": "request-1",
            },
        }
    )

    assert isinstance(response.cards[0], MandiRankingCard)
