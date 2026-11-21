from pydantic import Field

from .common import APIModel, LocalizedText


class ChatRequest(APIModel):
    message: str = Field(min_length=1, max_length=1000)
    language: str = Field(default="en", pattern="^(en|mr|hi)$")
    crop_id: str | None = None
    farmer_location: tuple[float, float] | None = None


class ChatResponse(APIModel):
    intent: str = Field(pattern="^(best_mandi|price_today|sell_or_wait|which_crop|help)$")
    answer: LocalizedText
    suggestion_chips: list[str]
