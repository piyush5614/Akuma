from typing import Annotated, Literal

from pydantic import Field

from .common import APIModel, LocalizedText


class ChatContext(APIModel):
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    crop_id: str | None = None
    quantity_quintal: float | None = Field(default=None, gt=0, le=10000)
    last_recommendation_id: str | None = None


class ChatClient(APIModel):
    platform: Literal["android", "web"] = "android"
    app_version: str = "1.0.0"
    device_id: str | None = Field(default=None, min_length=1, max_length=80)


class SaathiChatRequest(APIModel):
    session_id: str | None = Field(default=None, min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=500)
    input_mode: Literal["text", "voice"] = "text"
    ui_language: Literal["en", "mr", "hi", "auto"] = "auto"
    context: ChatContext = Field(default_factory=ChatContext)
    client: ChatClient = Field(default_factory=ChatClient)


class MandiRankingCard(APIModel):
    type: Literal["mandi_ranking"]
    data: dict


class TrendCard(APIModel):
    type: Literal["trend"]
    data: dict


class SeasonalityCard(APIModel):
    type: Literal["seasonality"]
    data: dict


class CropSuggestionsCard(APIModel):
    type: Literal["crop_suggestions"]
    data: dict


class TermCard(APIModel):
    type: Literal["term"]
    data: dict


ChatCard = Annotated[
    MandiRankingCard | TrendCard | SeasonalityCard | CropSuggestionsCard | TermCard,
    Field(discriminator="type"),
]


class ChatReply(APIModel):
    text: str
    speak_text: str
    language: Literal["en", "mr", "hi"]
    script: Literal["latin", "devanagari"]


class ChatMeta(APIModel):
    intent: str
    tools_used: list[str] = Field(default_factory=list)
    data_as_of: str | None = None
    is_demo: bool
    confidence: float = Field(ge=0, le=1)
    grounded: bool
    fallback_used: bool
    request_id: str


class SaathiChatResponse(APIModel):
    session_id: str
    reply: ChatReply
    cards: list[ChatCard] = Field(default_factory=list)
    chips: list[str] = Field(default_factory=list)
    meta: ChatMeta


class ChatStarter(APIModel):
    label: str
    message: str


class ChatFeedbackRequest(APIModel):
    request_id: str = Field(min_length=1, max_length=80)
    rating: Literal["up", "down"]
    reason_code: str | None = Field(default=None, max_length=80)


class ChatFeedbackResponse(APIModel):
    accepted: bool


# Legacy contract retained until the runtime endpoint is migrated in Part 4.
class ChatRequest(APIModel):
    message: str = Field(min_length=1, max_length=1000)
    language: str = Field(default="en", pattern="^(en|mr|hi)$")
    crop_id: str | None = None
    farmer_location: tuple[float, float] | None = None


class ChatResponse(APIModel):
    intent: str = Field(pattern="^(best_mandi|price_today|sell_or_wait|which_crop|help)$")
    answer: LocalizedText
    suggestion_chips: list[str]
