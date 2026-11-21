import os
from decimal import Decimal


class Settings:
    api_version = "1.0.0"
    min_app_version = "1.0.0"
    is_demo = True
    road_factor = Decimal(os.getenv("ROAD_FACTOR", "1.3"))
    transport_rate = Decimal(os.getenv("TRANSPORT_RATE_PER_QUINTAL_KM", "0.60"))
    fee_pct = Decimal(os.getenv("FEE_PCT", "0.01"))
    jwt_secret = os.getenv("JWT_SECRET", "change-me")


settings = Settings()
