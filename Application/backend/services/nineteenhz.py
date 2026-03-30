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
        event = _parse_row(row)
        if not event:
            continue

        # Filter: SF only, future events, keyword match
        city = event.pop("_city", "").lower()
        if city not in ("san francisco", "sf"):
            continue
        if event["end"] and event["end"] < now:
            continue
        tags = event.pop("_tags", "")
        if not _matches_keyword(event["name"], tags, keyword_lower):
            continue

        results.append(event)

    results.sort(key=lambda e: e["start"])
    return results


def _parse_row(row) -> dict | None:
    """Parse a single table row into an event dict.

    19hz's HTML is malformed — the first <td> often contains the content
    of all subsequent cells baked into its innerHTML. We parse from the
    raw row HTML instead of relying on clean <td> separation.
    """
    try:
        row_html = row.decode_contents()

        # Extract sort date from hidden div
        sort_match = re.search(
            r'<div class=["\']shrink["\']>(\d{4}/\d{2}/\d{2})</div>', row_html
        )
        if not sort_match:
            return None
        sort_date = sort_match.group(1)
        base_date = sort_date.replace("/", "-")

        # Extract first <td> for date/time
        first_cell = row.find("td")
        if not first_cell:
            return None
        date_text = first_cell.get_text(separator=" ", strip=True)
        start_time, end_time = _parse_time_range(date_text, base_date)

        # Extract event link and name from first <a> tag in second cell area
        # The first <a> after the first </td> is the event link
        links = row.find_all("a")
        event_url = ""
        event_name = ""
        if links:
            event_url = links[0].get("href", "")
            event_name = links[0].get_text(strip=True)

        # Extract venue and city: pattern is "Event Name</a> @ Venue (City)"
        # Look in the raw HTML after the closing </a> tag
        venue = "Venue TBD"
        city = ""
        venue_match = re.search(
            r"</a>\s*@\s*([^<]+?)(?:\(([^)]+)\))", row_html
        )
        if venue_match:
            venue = venue_match.group(1).strip() or "Venue TBD"
            city = venue_match.group(2).strip()

        # Extract tags from the second <td> content area
        # Tags appear after the venue/city, in the next <td>
        tags = ""
        td_tags_match = re.search(
            r"\((?:San Francisco|SF|Oakland|Berkeley|San Jose|Sacramento)[^)]*\)<td>([^<]*)</td>",
            row_html,
            re.IGNORECASE,
        )
        if td_tags_match:
            tags = td_tags_match.group(1).strip()

        # Extract price from the third <td> after the tags
        price_range = "See listing"
        # Find all <td> content after the event link area
        td_contents = re.findall(r"<td>([^<]*)</td>", row_html)
        if len(td_contents) >= 2:
            tags = tags or td_contents[0].strip()
            price_text = td_contents[1].strip()
            price_range = _parse_price(price_text)
        elif len(td_contents) >= 1 and not tags:
            tags = td_contents[0].strip()

        is_free = price_range.lower() == "free"

        return {
            "id": f"19hz-{sort_date.replace('/', '')}-{hash(event_name) % 100000}",
            "name": event_name,
            "summary": tags,
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


def _parse_time_range(date_text: str, base_date: str) -> tuple[str, str]:
    """Extract start and end ISO datetimes from date text and sort date."""
    time_match = re.search(
        r"\((?:[A-Za-z]+:\s*)?(\d{1,2}(?::\d{2})?\s*[ap]m)\s*-\s*(\d{1,2}(?::\d{2})?\s*[ap]m)\)",
        date_text,
        re.IGNORECASE,
    )
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


def _parse_price(price_text: str) -> str:
    """Parse price from varied formats."""
    if not price_text:
        return "See listing"

    # Split on pipe to separate price from age
    price_part = price_text.split("|")[0].strip()

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


def _matches_keyword(name: str, tags: str, keyword: str) -> bool:
    """Check if event name or tags contain the keyword."""
    return keyword in name.lower() or keyword in tags.lower()
