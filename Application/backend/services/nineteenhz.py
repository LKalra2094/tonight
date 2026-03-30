import re
from datetime import datetime

import httpx
from bs4 import BeautifulSoup


NINETEENHZ_URL = "https://19hz.info/eventlisting_BayArea.php"
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


async def search_events(keyword: str) -> list[dict]:
    """Fetch and parse 19hz Bay Area event listings, filtered by keyword."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            NINETEENHZ_URL, headers=BROWSER_HEADERS, timeout=15.0
        )
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    if not table:
        return []

    tbody = table.find("tbody")
    if not tbody:
        return []

    rows = tbody.find_all("tr")
    keyword_lower = keyword.lower()
    now = datetime.now().isoformat()
    results = []

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 7:
            continue

        event = _parse_row(cells)
        if not event:
            continue

        # Filter: SF only, future events, keyword match
        if event["_city"].lower() != "san francisco" and event["_city"].lower() != "sf":
            continue
        if event["end"] and event["end"] < now:
            continue
        if not _matches_keyword(event, keyword_lower):
            continue

        # Remove internal fields
        event.pop("_city", None)
        event.pop("_tags", None)
        results.append(event)

    results.sort(key=lambda e: e["start"])
    return results


def _parse_row(cells: list) -> dict | None:
    """Parse a single table row into an event dict."""
    try:
        # Column 6: hidden sort date
        sort_div = cells[6].find("div", class_="shrink")
        if not sort_div:
            return None
        sort_date = sort_div.get_text(strip=True)  # e.g., "2026/03/29"

        # Column 0: date and time range
        date_text = cells[0].get_text(separator=" ", strip=True)
        start_time, end_time = _parse_time_range(date_text, sort_date)

        # Column 1: event title + venue
        link = cells[1].find("a")
        event_url = link["href"] if link else ""
        event_name = link.get_text(strip=True) if link else ""

        cell_text = cells[1].get_text(separator=" ", strip=True)
        venue, city = _parse_venue_city(cell_text)

        # Column 2: tags
        tags = cells[2].get_text(strip=True)

        # Column 3: price | age
        price_age = cells[3].get_text(strip=True)
        price_range = _parse_price(price_age)
        is_free = price_range.lower() == "free"

        return {
            "id": f"19hz-{sort_date.replace('/', '')}-{hash(event_name) % 100000}",
            "name": event_name,
            "summary": f"{tags}" if tags else "",
            "start": start_time,
            "end": end_time,
            "timezone": "America/Los_Angeles",
            "venue": venue,
            "address": "",
            "neighborhood": "",
            "latitude": None,
            "longitude": None,
            "image_url": "",
            "is_free": is_free,
            "price_range": price_range,
            "tickets": [],
            "url": event_url,
            "source": "19hz",
            "_city": city,
            "_tags": tags,
        }
    except Exception:
        return None


def _parse_time_range(date_text: str, sort_date: str) -> tuple[str, str]:
    """Extract start and end ISO datetimes from date text and sort date."""
    # sort_date is like "2026/03/29"
    base_date = sort_date.replace("/", "-")

    # Time range pattern like "(9pm-2am)" or "(2pm-6pm)"
    time_match = re.search(r"\((\d{1,2}(?::\d{2})?\s*[ap]m)\s*-\s*(\d{1,2}(?::\d{2})?\s*[ap]m)\)", date_text, re.IGNORECASE)
    if time_match:
        start_str = time_match.group(1).strip()
        end_str = time_match.group(2).strip()
        start_time = _parse_time(start_str)
        end_time = _parse_time(end_str)
        return f"{base_date}T{start_time}", f"{base_date}T{end_time}"

    return f"{base_date}T00:00:00", f"{base_date}T23:59:59"


def _parse_time(time_str: str) -> str:
    """Convert '9pm' or '10:30pm' to '21:00:00' format."""
    time_str = time_str.lower().strip()
    try:
        if ":" in time_str:
            dt = datetime.strptime(time_str, "%I:%M%p")
        else:
            dt = datetime.strptime(time_str, "%I%p")
        return dt.strftime("%H:%M:%S")
    except ValueError:
        return "00:00:00"


def _parse_venue_city(cell_text: str) -> tuple[str, str]:
    """Extract venue and city from 'Event Name @ Venue (City)' text."""
    # Split on @ to get venue part
    parts = cell_text.split("@", 1)
    if len(parts) < 2:
        return "Venue TBD", ""

    venue_part = parts[1].strip()

    # Extract city from parentheses at end
    city_match = re.search(r"\(([^)]+)\)\s*$", venue_part)
    city = city_match.group(1).strip() if city_match else ""

    # Venue is everything before the city parentheses
    if city_match:
        venue = venue_part[: city_match.start()].strip()
    else:
        venue = venue_part.strip()

    return venue or "Venue TBD", city


def _parse_price(price_age: str) -> str:
    """Parse price from '20' or '$5 b4 10/$10' or 'free' or '$20-30 | 21+'."""
    if not price_age:
        return "See listing"

    # Split on pipe to separate price from age
    price_part = price_age.split("|")[0].strip()

    if not price_part:
        return "See listing"

    if price_part.lower() == "free":
        return "Free"

    # Find all dollar amounts
    amounts = re.findall(r"\$?(\d+(?:\.\d{2})?)", price_part)
    if not amounts:
        return "See listing"

    prices = [float(a) for a in amounts]
    low = min(prices)
    high = max(prices)

    if low == 0:
        return "Free" if high == 0 else f"Free – ${high:.0f}"
    if low == high:
        return f"${low:.0f}"
    return f"${low:.0f} – ${high:.0f}"


def _matches_keyword(event: dict, keyword: str) -> bool:
    """Check if event name or tags contain the keyword."""
    name = event.get("name", "").lower()
    tags = event.get("_tags", "").lower()
    return keyword in name or keyword in tags
