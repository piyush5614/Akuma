from decimal import Decimal

from ..schemas.common import LocalizedText


def decide(slope_pct_day: Decimal, arrivals_change_pct: Decimal, seasonal_rise_pct: Decimal, perishable: bool) -> dict:
    reasons: list[str] = []
    if slope_pct_day > 1 and arrivals_change_pct < -10:
        reasons.append("RISING_PRICE_FALLING_ARRIVALS")
    if seasonal_rise_pct > 5 and slope_pct_day >= 0:
        reasons.append("SEASONAL_RISE")
    if reasons:
        decision = "WAIT"
    else:
        if slope_pct_day < -1:
            reasons.append("FALLING_PRICE")
        if arrivals_change_pct > 15 and slope_pct_day <= 0:
            reasons.append("RISING_ARRIVALS")
        if perishable:
            reasons.append("HIGH_PERISHABILITY")
        decision = "SELL_NOW" if reasons else "UNSURE"
    messages = {
        "WAIT": LocalizedText(en="Prices may improve; consider waiting.", mr="भाव वाढू शकतात; थांबण्याचा विचार करा.", hi="भाव बढ़ सकते हैं; रुकने पर विचार करें."),
        "SELL_NOW": LocalizedText(en="Selling now may reduce price risk.", mr="आत्ता विकल्याने भावाचा धोका कमी होऊ शकतो.", hi="अभी बेचने से भाव का जोखिम कम हो सकता है."),
        "UNSURE": LocalizedText(en="The signal is mixed; check again tomorrow.", mr="संकेत मिश्र आहेत; उद्या पुन्हा तपासा.", hi="संकेत मिश्रित हैं; कल फिर जाँचें."),
    }
    return {"decision": decision, "reason_codes": reasons or ["INSUFFICIENT_SIGNAL"], "reason": messages[decision], "disclaimer": "Guidance, not a guarantee"}
