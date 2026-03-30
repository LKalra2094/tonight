import httpx
from typing import Optional


EVENTBRITE_BASE_URL = "https://www.eventbriteapi.com/v3"


async def search_events(api_key: str, keyword: str) -> list[dict]:
    """Search Eventbrite for events in San Francisco matching a keyword."""
    url = f"{EVENTBRITE_BASE_URL}/events/search/"
    params = {
        "q": keyword,
        "location.address": "San Francisco, CA",
        "location.within": "10mi",
        "sort_by": "date",
        "expand": "venue,ticket_availability",
    }
    headers = {"Authorization": f"Bearer {api_key}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers, timeout=15.0)
        response.raise_for_status()
        data = response.json()

    events = data.get("events", [])
    return [_format_event(event) for event in events[:20]]


def _format_event(event: dict) -> dict:
    """Transform an Eventbrite event into our response shape."""
    venue = event.get("venue") or {}
    address_parts = []
    addr = venue.get("address", {})
    if addr.get("address_1"):
        address_parts.append(addr["address_1"])
    if addr.get("city"):
        address_parts.append(addr["city"])
    if addr.get("region"):
        address_parts.append(addr["region"])

    price = _get_price(event)

    return {
        "id": event.get("id", ""),
        "name": event.get("name", {}).get("text", "Untitled Event"),
        "start": event.get("start", {}).get("local", ""),
        "end": event.get("end", {}).get("local", ""),
        "venue": venue.get("name", "Venue TBD"),
        "address": ", ".join(address_parts) if address_parts else "Address TBD",
        "price": price,
        "url": event.get("url", ""),
        "source": "Eventbrite",
    }


def _get_price(event: dict) -> str:
    """Extract price from ticket availability or fall back to is_free flag."""
    if event.get("is_free"):
        return "Free"

    ticket_availability = event.get("ticket_availability", {})
    min_price = ticket_availability.get("minimum_ticket_price")
    if min_price and min_price.get("major_value"):
        return f"${min_price['major_value']}"

    return "See listing"
