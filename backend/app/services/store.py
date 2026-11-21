from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

TODAY = date.today()
CROPS = [
    {"id": "onion", "name": {"en": "Onion", "mr": "कांदा", "hi": "प्याज"}, "unit": "quintal", "perishability": "high"},
    {"id": "tomato", "name": {"en": "Tomato", "mr": "टोमॅटो", "hi": "टमाटर"}, "unit": "quintal", "perishability": "high"},
    {"id": "soybean", "name": {"en": "Soybean", "mr": "सोयाबीन", "hi": "सोयाबीन"}, "unit": "quintal", "perishability": "low"},
]
MANDIS = [
    {"id": "pune", "name": "Pune", "district": "Pune", "state": "Maharashtra", "location": {"lat": 18.52, "lng": 73.86}, "prices": {"onion": Decimal(2400), "tomato": Decimal(1800), "soybean": Decimal(4600)}, "age": 0},
    {"id": "nashik", "name": "Nashik", "district": "Nashik", "state": "Maharashtra", "location": {"lat": 20.00, "lng": 73.78}, "prices": {"onion": Decimal(2500), "tomato": Decimal(1700), "soybean": Decimal(4500)}, "age": 2},
    {"id": "satara", "name": "Satara", "district": "Satara", "state": "Maharashtra", "location": {"lat": 17.68, "lng": 74.02}, "prices": {"onion": Decimal(2300), "tomato": Decimal(1900), "soybean": Decimal(4400)}, "age": 10},
]


def as_of() -> datetime:
    return datetime.now(UTC)


def report_date(mandi: dict) -> date:
    return TODAY - timedelta(days=mandi["age"])
