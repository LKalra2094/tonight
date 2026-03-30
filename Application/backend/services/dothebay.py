import asyncio

import httpx


DOTHEBAY_BASE_URL = "https://dothebay.com/events/today"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


async def search_events(keyword: str) -> list[dict]:
    """Fetch today's events from Do The Bay and filter by keyword."""
    async with httpx.AsyncClient() as client:
        # Fetch first page to get pagination info
        response = await client.get(
            DOTHEBAY_BASE_URL, headers=HEADERS, timeout=15.0
        )
        response.raise_for_status()
        data = response.json()

    events = data.get("events", [])
    paging = data.get("paging", {})
    total_pages = paging.get("total_pages", 1)

    # Fetch remaining pages concurrently
    if total_pages > 1:
        async with httpx.AsyncClient() as client:
            tasks = [
                client.get(
                    f"{DOTHEBAY_BASE_URL}?page={page}",
                    headers=HEADERS,
                    timeout=15.0,
                )
                for page in range(2, total_pages + 1)
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            for resp in responses:
                if isinstance(resp, Exception):
                    continue
                try:
                    resp.raise_for_status()
                    page_data = resp.json()
                    events.extend(page_data.get("events", []))
                except Exception:
                    continue

    keyword_lower = keyword.lower()
    results = []
    for event in events:
        if event.get("sold_out"):
            continue
        if _matches_keyword(event, keyword_lower):
            results.append(_format_event(event))

    results.sort(key=lambda e: e["start"])
    return results


def _matches_keyword(event: dict, keyword: str) -> bool:
    """Check if event title or excerpt contains the keyword."""
    title = (event.get("title") or "").lower()
    excerpt = (event.get("excerpt") or "").lower()
    category = (event.get("category") or "").lower()
    return keyword in title or keyword in excerpt or keyword in category


def _format_event(event: dict) -> dict:
    """Transform a Do The Bay event into our unified response shape."""
    venue = event.get("venue") or {}
    imagery = event.get("imagery") or {}
    aws = imagery.get("aws") or {}

    # Pick best available image
    image_url = (
        aws.get("cover_image_h_630_w_1200")
        or aws.get("cover_image_h_300_w_864")
        or aws.get("cover_image_h_50_w_50")
        or ""
    )

    start = event.get("tz_adjusted_begin_date", "")
    end = event.get("tz_adjusted_end_date", "")
    is_free = event.get("is_free", False)

    # Build URL
    permalink = event.get("permalink", "")
    url = f"https://dothebay.com{permalink}" if permalink else ""

    # Buy URL takes priority if available
    buy_url = event.get("buy_url") or url

    return {
        "id": str(event.get("id", "")),
        "name": event.get("title", "Untitled Event"),
        "summary": event.get("excerpt", ""),
        "start": start,
        "end": end,
        "timezone": "America/Los_Angeles",
        "venue": venue.get("title", "Venue TBD"),
        "address": venue.get("full_address", ""),
        "neighborhood": "",
        "latitude": venue.get("latitude"),
        "longitude": venue.get("longitude"),
        "image_url": image_url,
        "is_free": is_free,
        "price_range": _get_price_range(event),
        "tickets": [],
        "url": buy_url,
        "source": "Do The Bay",
    }


def _get_price_range(event: dict) -> str:
    """Extract price range from ticket_info string."""
    if event.get("is_free"):
        return "Free"

    ticket_info = event.get("ticket_info", "")
    if not ticket_info:
        return "See listing"

    # ticket_info is like "$23, All ages" or "Free, 21+"
    if "free" in ticket_info.lower():
        return "Free"

    # Extract dollar amount from the string
    import re

    amounts = re.findall(r"\$(\d+(?:\.\d{2})?)", ticket_info)
    if amounts:
        prices = [float(a) for a in amounts]
        low = min(prices)
        high = max(prices)
        if low == high:
            return f"${low:.0f}"
        return f"${low:.0f} – ${high:.0f}"

    return ticket_info.split(",")[0].strip() or "See listing"
