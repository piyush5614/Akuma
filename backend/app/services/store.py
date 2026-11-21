from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

TODAY = date.today()
CROPS = [
    {"id": "onion", "name": {"en": "Onion", "mr": "कांदा", "hi": "प्याज"}, "category": "vegetable", "unit": "quintal", "perishability": "high"},
    {"id": "tomato", "name": {"en": "Tomato", "mr": "टोमॅटो", "hi": "टमाटर"}, "category": "vegetable", "unit": "quintal", "perishability": "high"},
    {"id": "potato", "name": {"en": "Potato", "mr": "बटाटा", "hi": "आलू"}, "category": "vegetable", "unit": "quintal", "perishability": "medium"},
    {"id": "cabbage", "name": {"en": "Cabbage", "mr": "कोबी", "hi": "पत्तागोभी"}, "category": "vegetable", "unit": "quintal", "perishability": "high"},
    {"id": "cauliflower", "name": {"en": "Cauliflower", "mr": "फ्लॉवर", "hi": "फूलगोभी"}, "category": "vegetable", "unit": "quintal", "perishability": "high"},
    {"id": "okra", "name": {"en": "Okra", "mr": "भेंडी", "hi": "भिंडी"}, "category": "vegetable", "unit": "quintal", "perishability": "high"},
    {"id": "brinjal", "name": {"en": "Brinjal", "mr": "वांगी", "hi": "बैंगन"}, "category": "vegetable", "unit": "quintal", "perishability": "high"},
    {"id": "green_chilli", "name": {"en": "Green chilli", "mr": "हिरवी मिरची", "hi": "हरी मिर्च"}, "category": "vegetable", "unit": "quintal", "perishability": "high"},
    {"id": "wheat", "name": {"en": "Wheat", "mr": "गहू", "hi": "गेहूं"}, "category": "grain", "unit": "quintal", "perishability": "low"},
    {"id": "rice", "name": {"en": "Rice", "mr": "तांदूळ", "hi": "चावल"}, "category": "grain", "unit": "quintal", "perishability": "low"},
    {"id": "maize", "name": {"en": "Maize", "mr": "मका", "hi": "मक्का"}, "category": "grain", "unit": "quintal", "perishability": "low"},
    {"id": "soybean", "name": {"en": "Soybean", "mr": "सोयाबीन", "hi": "सोयाबीन"}, "category": "grain", "unit": "quintal", "perishability": "low"},
    {"id": "jowar", "name": {"en": "Jowar", "mr": "ज्वारी", "hi": "ज्वार"}, "category": "grain", "unit": "quintal", "perishability": "low"},
    {"id": "gram", "name": {"en": "Gram", "mr": "हरभरा", "hi": "चना"}, "category": "grain", "unit": "quintal", "perishability": "low"},
    {"id": "banana", "name": {"en": "Banana", "mr": "केळी", "hi": "केला"}, "category": "fruit", "unit": "quintal", "perishability": "high"},
    {"id": "mango", "name": {"en": "Mango", "mr": "आंबा", "hi": "आम"}, "category": "fruit", "unit": "quintal", "perishability": "high"},
    {"id": "pomegranate", "name": {"en": "Pomegranate", "mr": "डाळिंब", "hi": "अनार"}, "category": "fruit", "unit": "quintal", "perishability": "medium"},
    {"id": "grapes", "name": {"en": "Grapes", "mr": "द्राक्षे", "hi": "अंगूर"}, "category": "fruit", "unit": "quintal", "perishability": "high"},
    {"id": "orange", "name": {"en": "Orange", "mr": "संत्रे", "hi": "संतरा"}, "category": "fruit", "unit": "quintal", "perishability": "medium"},
]
DEFAULT_PRICES = {
    "potato": Decimal(1700), "cabbage": Decimal(1500), "cauliflower": Decimal(2200),
    "okra": Decimal(3200), "brinjal": Decimal(2100), "green_chilli": Decimal(4200),
    "wheat": Decimal(2600), "rice": Decimal(3000), "maize": Decimal(2200),
    "jowar": Decimal(3200), "gram": Decimal(5800), "banana": Decimal(2100),
    "mango": Decimal(4500), "pomegranate": Decimal(7000), "grapes": Decimal(5000),
    "orange": Decimal(3600),
}
MANDIS = [
    {"id": "pune", "name": "Pune", "district": "Pune", "state": "Maharashtra", "location": {"lat": 18.52, "lng": 73.86}, "prices": {"onion": Decimal(2400), "tomato": Decimal(1800), "soybean": Decimal(4600)}, "age": 0},
    {"id": "nashik", "name": "Nashik", "district": "Nashik", "state": "Maharashtra", "location": {"lat": 20.00, "lng": 73.78}, "prices": {"onion": Decimal(2500), "tomato": Decimal(1700), "soybean": Decimal(4500)}, "age": 2},
    {"id": "satara", "name": "Satara", "district": "Satara", "state": "Maharashtra", "location": {"lat": 17.68, "lng": 74.02}, "prices": {"onion": Decimal(2300), "tomato": Decimal(1900), "soybean": Decimal(4400)}, "age": 10},
]
for _mandi in MANDIS:
    for _crop in CROPS:
        _mandi["prices"].setdefault(_crop["id"], DEFAULT_PRICES.get(_crop["id"], Decimal(2000)))


def as_of() -> datetime:
    return datetime.now(UTC)


def report_date(mandi: dict) -> date:
    return TODAY - timedelta(days=mandi["age"])
