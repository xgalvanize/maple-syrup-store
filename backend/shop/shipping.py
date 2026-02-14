def _normalize(value: str) -> str:
    return (value or "").strip().upper()


def estimate_shipping(country: str, region: str, postal: str) -> tuple[int, str]:
    country_code = _normalize(country)
    region_code = _normalize(region)
    postal_code = _normalize(postal).replace(" ", "")
    postal_prefix = postal_code[:3]

    if country_code not in {"CA", "CANADA"}:
        return 2999, "INTERNATIONAL"

    if region_code not in {"ON", "ONTARIO"}:
        return 1299, "CANADA"

    if postal_prefix == "P0R":
        return 499, "LOCAL_RADIUS"

    return 799, "ONTARIO"


def calculate_shipping_cents(country: str, region: str, postal: str) -> int:
    cents, _ = estimate_shipping(country, region, postal)
    return cents
