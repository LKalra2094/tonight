from apify_client import ApifyClient


INSTAGRAM_ACCOUNTS = [
    "andrewtourssf",
    "secret_sanfrancisco",
    "onlyinsf",
    "sfbaydiaries",
    "sfgirl.chronicle",
    "sfstandard",
    "sfbucketlist",
]

ACTOR_ID = "apify/instagram-post-scraper"


async def search_events(apify_token: str, keyword: str) -> list[dict]:
    """Fetch recent Instagram posts from SF accounts and filter by keyword."""
    client = ApifyClient(apify_token)

    # Apify client is synchronous — run in the default executor
    import asyncio

    loop = asyncio.get_event_loop()
    items = await loop.run_in_executor(
        None, lambda: _fetch_posts(client)
    )

    keyword_lower = keyword.lower()
    results = []
    for item in items:
        caption = (item.get("caption") or "").lower()
        if keyword_lower not in caption:
            continue
        formatted = _format_post(item)
        if formatted:
            results.append(formatted)

    results.sort(key=lambda e: e["start"], reverse=True)
    return results


def _fetch_posts(client: ApifyClient) -> list[dict]:
    """Run the Apify Instagram Post Scraper and return all items."""
    run = client.actor(ACTOR_ID).call(
        run_input={
            "username": INSTAGRAM_ACCOUNTS,
            "resultsLimit": 30,
        },
        timeout_secs=120,
    )

    dataset_id = run.get("defaultDatasetId")
    if not dataset_id:
        return []

    return list(client.dataset(dataset_id).iterate_items())


def _format_post(item: dict) -> dict | None:
    """Transform an Apify Instagram post into our unified event schema."""
    caption = item.get("caption") or ""
    timestamp = item.get("timestamp") or ""
    post_url = item.get("url") or ""
    image_url = item.get("displayUrl") or ""

    if not caption:
        return None

    # Use first line of caption as event name (truncated at 80 chars)
    first_line = caption.split("\n")[0].strip()
    name = first_line[:80] if len(first_line) > 80 else first_line
    if not name:
        name = "Instagram Post"

    owner = item.get("ownerUsername") or ""

    return {
        "id": f"ig-{item.get('id', '')}",
        "name": name,
        "summary": caption[:500] if len(caption) > 500 else caption,
        "start": timestamp,
        "end": "",
        "timezone": "America/Los_Angeles",
        "venue": f"@{owner}" if owner else "Instagram",
        "address": "",
        "neighborhood": "",
        "latitude": None,
        "longitude": None,
        "image_url": image_url,
        "is_free": False,
        "price_range": "See listing",
        "tickets": [],
        "url": post_url,
        "source": "Instagram",
    }
