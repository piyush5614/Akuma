from datetime import date


def freshness(report_date: date | None, today: date | None = None) -> str:
    if report_date is None:
        return "NO_REPORT"
    today = today or date.today()
    age = (today - report_date).days
    if age <= 1:
        return "FRESH"
    if age <= 7:
        return "STALE"
    return "OLD"
