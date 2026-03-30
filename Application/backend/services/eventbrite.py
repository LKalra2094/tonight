import asyncio
import json
import re
from datetime import datetime

import httpx


EVENTBRITE_BASE_URL = "https://www.eventbriteapi.com/v3"
EVENTBRITE_SEARCH_URL = "https://www.eventbrite.com/d/ca--san-francisco/{keyword}/"
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


async def search_events(api_key: str, keyword: str) -> list[dict]:
    """Scrape Eventbrite search results and enrich with ticket data."""
    url = EVENTBRITE_SEARCH_URL.format(keyword=keyword.replace(" ", "-"))

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url, headers=BROWSER_HEADERS, timeout=15.0, follow_redirects=True
        )
        response.raise_for_status()

    server_data = _extract_server_data(response.text)
    if not server_data:
        return []

    events = (
        server_data.get("search_data", {})
        .get("events", {})
        .get("results", [])
    )

    # Extract IDs and fetch ticket data
    event_ids = [e.get("id") for e in events if e.get("id")]
    ticket_map = await _fetch_all_tickets(api_key, event_ids)

    now = datetime.now().isoformat()
    results = []
    for event in events:
        formatted = _format_event(event, ticket_map.get(event.get("id"), {}))
        if formatted["end"] > now:
            results.append(formatted)

    results.sort(key=lambda e: e["start"])
    return results


async def _fetch_all_tickets(
    api_key: str, event_ids: list[str]
) -> dict[str, dict]:
    """Fetch ticket classes for all event IDs concurrently."""
    async with httpx.AsyncClient() as client:
        tasks = {
            eid: client.get(
                f"{EVENTBRITE_BASE_URL}/events/{eid}/ticket_classes/",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0,
            )
            for eid in event_ids
        }
        results = {}
        responses = await asyncio.gather(
            *tasks.values(), return_exceptions=True
        )
        for eid, resp in zip(tasks.keys(), responses):
            if isinstance(resp, Exception):
                results[eid] = {}
            else:
                try:
                    resp.raise_for_status()
                    results[eid] = resp.json()
                except Exception:
                    results[eid] = {}
        return results


def _extract_server_data(html: str) -> dict | None:
    """Extract the window.__SERVER_DATA__ JSON from the page HTML."""
    match = re.search(
        r"window\.__SERVER_DATA__\s*=\s*({.*?});", html, re.DOTALL
    )
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def _format_event(event: dict, tickets_data: dict) -> dict:
    """Transform a scraped Eventbrite event into our response shape."""
    venue = event.get("primary_venue") or {}
    address = venue.get("address", {})
    image = event.get("image") or {}

    tickets = _format_tickets(tickets_data)
    price_range = _get_price_range(tickets)

    return {
        "id": event.get("id", ""),
        "name": event.get("name", "Untitled Event"),
        "summary": event.get("summary", ""),
        "start": f"{event.get('start_date', '')}T{event.get('start_time', '')}",
        "end": f"{event.get('end_date', '')}T{event.get('end_time', '')}",
        "timezone": event.get("timezone", ""),
        "venue": venue.get("name", "Venue TBD"),
        "address": address.get("localized_address_display", "Address TBD"),
        "neighborhood": address.get("neighborhood", ""),
        "latitude": address.get("latitude"),
        "longitude": address.get("longitude"),
        "image_url": image.get("original", {}).get("url", ""),
        "is_free": event.get("is_free", False),
        "price_range": price_range,
        "tickets": tickets,
        "url": event.get("url", ""),
        "source": "Eventbrite",
    }


def _format_tickets(tickets_data: dict) -> list[dict]:
    """Extract ticket classes into a clean list."""
    result = []
    for tc in tickets_data.get("ticket_classes", []):
        if tc.get("category") == "add_on":
            continue
        cost = tc.get("cost")
        result.append({
            "name": tc.get("display_name", ""),
            "price": cost.get("display") if cost else "Free",
            "free": tc.get("free", False),
            "status": tc.get("on_sale_status", ""),
        })
    return result


def _get_price_range(tickets: list[dict]) -> str:
    """Build a human-readable price range from ticket classes."""
    if not tickets:
        return "See listing"

    if all(t["free"] for t in tickets):
        return "Free"

    prices = []
    for t in tickets:
        if t["free"]:
            prices.append(0)
        elif t["price"] and t["price"] != "Free":
            try:
                prices.append(
                    float(t["price"].replace("$", "").replace(",", ""))
                )
            except ValueError:
                continue

    if not prices:
        return "See listing"

    low = min(prices)
    high = max(prices)

    if low == 0 and high > 0:
        return f"Free – ${high:.0f}"
    if low == high:
        return f"${low:.0f}"
    return f"${low:.0f} – ${high:.0f}"
