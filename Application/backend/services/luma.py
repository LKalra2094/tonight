from datetime import datetime

import httpx


LUMA_API_URL = "https://api.lu.ma/discover/get-paginated-events"


async def search_events(keyword: str) -> list[dict]:
    """Fetch SF events from Lu.ma and filter by keyword."""
    params = {"place": "sf"}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            LUMA_API_URL, params=params, timeout=15.0, follow_redirects=True
        )
        response.raise_for_status()
        data = response.json()

    entries = data.get("entries", [])
    now = datetime.now().isoformat()
    keyword_lower = keyword.lower()

    results = []
    for entry in entries:
        if _should_skip(entry, now):
            continue
        if _matches_keyword(entry, keyword_lower):
            results.append(_format_event(entry))

    results.sort(key=lambda e: e["start"])
    return results


def _should_skip(entry: dict, now: str) -> bool:
    """Skip past, sold out, invite-only, and online events."""
    event = entry.get("event", {})
    ticket = entry.get("ticket_info") or {}

    end = event.get("end_at", "")
    if end and end < now:
        return True
    if ticket.get("is_sold_out"):
        return True
    if event.get("location_type") == "online":
        return True

    return False


def _matches_keyword(entry: dict, keyword: str) -> bool:
    """Check if the event name or description contains the keyword."""
    event = entry.get("event", {})
    name = (event.get("name") or "").lower()
    desc = (event.get("description") or "").lower()
    return keyword in name or keyword in desc


def _format_event(entry: dict) -> dict:
    """Transform a Lu.ma event entry into our response shape."""
    event = entry.get("event", {})
    geo = event.get("geo_address_info") or {}
    ticket = entry.get("ticket_info") or {}

    start = event.get("start_at", "")
    end = event.get("end_at", "")
    slug = event.get("url", "")

    return {
        "id": slug,
        "name": event.get("name", "Untitled Event"),
        "summary": event.get("description", ""),
        "start": start,
        "end": end,
        "timezone": event.get("timezone", ""),
        "venue": geo.get("description", "Venue TBD"),
        "address": geo.get("full_address") or geo.get("city_state", "San Francisco"),
        "neighborhood": geo.get("sublocality", ""),
        "latitude": (event.get("coordinate") or {}).get("latitude"),
        "longitude": (event.get("coordinate") or {}).get("longitude"),
        "image_url": event.get("cover_url", ""),
        "is_free": ticket.get("is_free", False),
        "price_range": _get_price_range(ticket),
        "tickets": [],
        "url": f"https://lu.ma/{slug}",
        "source": "Lu.ma",
    }


def _get_price_range(ticket: dict) -> str:
    """Build price range from Lu.ma ticket info."""
    if ticket.get("is_free"):
        return "Free"

    price = ticket.get("price")
    if price and price.get("cents"):
        amount = price["cents"] / 100
        max_price = ticket.get("max_price")
        if max_price and max_price.get("cents") and max_price["cents"] != price["cents"]:
            max_amount = max_price["cents"] / 100
            return f"${amount:.0f} – ${max_amount:.0f}"
        return f"${amount:.0f}"

    if ticket.get("require_approval"):
        return "Invite only"

    return "See listing"
