from decimal import Decimal

from pydantic import Field

from .common import APIModel


class Meta(APIModel):
    api_version: str
    min_app_version: str
    is_demo: bool


class AdminSummary(APIModel):
    mandi_count: int
    crop_count: int
    report_count: int
    fresh_report_pct: Decimal
    query_count: int


class AdminSettings(APIModel):
    road_factor: Decimal = Field(gt=0)
    transport_rate_per_quintal_km: Decimal = Field(ge=0)
    fee_pct: Decimal = Field(ge=0, le=1)
    shrinkage_pct_by_crop: dict[str, Decimal]


class ImportResult(APIModel):
    imported_records: int
    skipped_records: int
    errors: list[str]


class QueryLog(APIModel):
    requested_at: str
    crop_id: str
    radius_km: Decimal
    location_rounded: tuple[Decimal, Decimal]


class QueryLogResponse(APIModel):
    items: list[QueryLog]
    total: int
