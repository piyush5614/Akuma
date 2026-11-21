from datetime import date, datetime
from decimal import Decimal
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class LocalizedText(APIModel):
    en: str
    mr: str
    hi: str


class ResponseMeta(APIModel):
    data_as_of: datetime
    is_demo: bool


class DataResponse(APIModel, Generic[T]):
    data: T
    data_as_of: datetime
    is_demo: bool


class ErrorResponse(APIModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class Coordinates(APIModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class Page(APIModel):
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class DateRange(APIModel):
    start: date
    end: date


class Money(APIModel):
    amount_inr: Decimal
    unit: str = "quintal"
