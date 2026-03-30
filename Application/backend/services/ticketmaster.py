import httpx


TICKETMASTER_URL = "https://app.ticketmaster.com/discovery/v2/events.json"


async def search_events(api_key: str, keyword: str) -> list[dict]:
    """Search Ticketmaster Discovery API for SF events by keyword."""
    params = {
        "apikey": api_key,
        "keyword": keyword,
        "city": "San Francisco",
        "stateCode": "CA",
        "countryCode": "US",
        "size": 50,
        "sort": "date,asc",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            TICKETMASTER_URL, params=params, timeout=15.0
        )
        response.raise_for_status()
        data = response.json()

    events = data.get("_embedded", {}).get("events", [])
    results = [_format_event(event) for event in events]
    results.sort(key=lambda e: e["start"])
    return results


def _format_event(event: dict) -> dict:
    """Transform a Ticketmaster event into our unified response shape."""
    dates = event.get("dates", {}).get("start", {})
    local_date = dates.get("localDate", "")
    local_time = dates.get("localTime", "00:00:00")

    start = f"{local_date}T{local_time}" if local_date else ""
    # Ticketmaster doesn't always provide end time
    end_dates = event.get("dates", {}).get("end", {})
    end_date = end_dates.get("localDate", local_date)
    end_time = end_dates.get("localTime", "")
    end = f"{end_date}T{end_time}" if end_date and end_time else ""

    venues = event.get("_embedded", {}).get("venues", [])
    venue = venues[0] if venues else {}
    venue_name = venue.get("name", "Venue TBD")
    address_line = venue.get("address", {}).get("line1", "")
    city = venue.get("city", {}).get("name", "")
    state = venue.get("state", {}).get("stateCode", "")
    address = ", ".join(filter(None, [address_line, city, state]))

    location = venue.get("location", {})
    latitude = _safe_float(location.get("latitude"))
    longitude = _safe_float(location.get("longitude"))

    image_url = _pick_image(event.get("images", []))
    price_range = _get_price_range(event.get("priceRanges", []))
    is_free = price_range.lower() == "free"

    return {
        "id": event.get("id", ""),
        "name": event.get("name", "Untitled Event"),
        "summary": "",
        "start": start,
        "end": end,
        "timezone": "America/Los_Angeles",
        "venue": venue_name,
        "address": address,
        "neighborhood": "",
        "latitude": latitude,
        "longitude": longitude,
        "image_url": image_url,
        "is_free": is_free,
        "price_range": price_range,
        "tickets": [],
        "url": event.get("url", ""),
        "source": "Ticketmaster",
    }


def _pick_image(images: list[dict]) -> str:
    """Pick the image closest to 600px wide."""
    if not images:
        return ""

    best = None
    best_diff = float("inf")
    for img in images:
        width = img.get("width", 0)
        diff = abs(width - 600)
        if diff < best_diff:
            best_diff = diff
            best = img

    return best["url"] if best else ""


def _get_price_range(price_ranges: list[dict]) -> str:
    """Build price range string from Ticketmaster priceRanges."""
    if not price_ranges:
        return "See listing"

    mins = []
    maxs = []
    for pr in price_ranges:
        if pr.get("min") is not None:
            mins.append(pr["min"])
        if pr.get("max") is not None:
            maxs.append(pr["max"])

    if not mins and not maxs:
        return "See listing"

    low = min(mins) if mins else 0
    high = max(maxs) if maxs else low

    if low == 0 and high == 0:
        return "Free"
    if low == high:
        return f"${low:.0f}"
    return f"${low:.0f} – ${high:.0f}"


def _safe_float(value) -> float | None:
    """Safely convert a value to float."""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
