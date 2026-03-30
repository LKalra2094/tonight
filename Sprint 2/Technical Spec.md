# Sprint 2 — Technical Spec: Event Source Expansion

**Created**: March 2026
**Status**: In Progress

---

## Goal

Make Tonight a genuinely useful SF event aggregator by adding four new event sources alongside the existing Eventbrite and Lu.ma integrations. After this sprint, a single keyword search returns events from six sources.

---

## Sources Overview

| Source | Method | What it adds | Auth |
|--------|--------|-------------|------|
| 19hz | HTML table scrape | Electronic music, underground events, raves | None |
| Do The Bay | JSON API (Accept header trick) | Curated local picks: pop-ups, markets, nightlife, free events | None |
| Ticketmaster | Discovery API v2 | Concerts, sports, theater, large-venue events | API key (free, 5000 req/day) |
| Instagram (8 accounts) | Apify Instagram Post Scraper | SF lifestyle/event posts from local creators and media | Apify API token (free tier, $5/mo credit) |

---

## Scope

### In Scope

- 19hz scraper: fetch and parse the Bay Area event listing table
- Do The Bay scraper: fetch events via JSON API for today/tomorrow/specific dates
- Ticketmaster integration: search SF events by keyword via Discovery API
- Instagram integration: pull recent posts from 8 accounts via Apify, extract event-like content
- All new sources output the same unified event schema used by Eventbrite and Lu.ma
- All sources called concurrently from the existing `/api/events` endpoint
- Update `.env.example` with new keys

### Out of Scope

- UI changes (same search bar, same event cards, same filters)
- LLM parsing of Instagram captions (plain text matching for now)
- Caching or background refresh of any source
- Deduplication across sources (same event on Eventbrite and Ticketmaster shows twice)

---

## Architecture

```
[React Frontend]
        │
        │  GET /api/events?q=comedy
        ▼
[FastAPI Backend]
        │
        ├── Eventbrite  (existing — scrape + ticket API)
        ├── Lu.ma       (existing — public REST API)
        ├── 19hz        (NEW — HTML table scrape)
        ├── Do The Bay  (NEW — JSON API)
        ├── Ticketmaster (NEW — Discovery API v2)
        └── Instagram   (NEW — Apify Post Scraper)
        │
        ▼
  Merge + sort by start time → return to frontend
```

All six sources are called concurrently via `asyncio.gather()`. Each source returns a list of events in the unified schema. Failures in any source are caught and skipped — the endpoint returns whatever it can.

---

## Source Details

### 19hz

**URL**: `https://19hz.info/eventlisting_BayArea.php`

**Approach**: Fetch the full HTML page, parse the `<table>` with BeautifulSoup. Each `<tr>` in `<tbody>` has 7 `<td>` columns:

| Column | Content |
|--------|---------|
| 0 | Date and time range (e.g., `Sat: Mar 29 (9pm-2am)`) |
| 1 | Event title as `<a href>` link + ` @ Venue Name (City)` |
| 2 | Genre tags (comma-separated) |
| 3 | Price and age (e.g., `$20 | 21+`) |
| 4 | Organizers |
| 5 | Additional links (Facebook, Instagram) |
| 6 | Hidden sort date (`<div class='shrink'>2026/03/29</div>`) |

**Keyword matching**: Match against event title and genre tags (case-insensitive substring).

**City filtering**: Only include events where the venue city is San Francisco (parsed from column 1, the text in parentheses after `@`).

**Price parsing**: Column 3 contains varied formats: `$20`, `$5 b4 10/$10`, `free`, `$20-30 | 21+`. Parse best-effort — extract dollar amounts, build a range string. Fall back to "See listing" if unparseable.

**No image data available from 19hz.**

**File**: `backend/services/nineteenhz.py`

### Do The Bay

**URL**: `https://dothebay.com/events/today` (or `/events/YYYY/M/D` for specific dates)

**Approach**: Send GET request with `Accept: application/json` header. The server returns JSON instead of HTML. No authentication needed.

**Response structure**:
```json
{
  "events": [...],
  "paging": { "total_pages": 5, "current_page": 1, "page_size": 25 }
}
```

**Pagination**: Fetch page 1 first. If `total_pages > 1`, fetch remaining pages concurrently.

**Keyword matching**: Do The Bay has no keyword search — it returns all events for a date. Filter client-side by matching keyword against event `title` and `excerpt` (case-insensitive substring).

**Category filtering**: Can optionally hit `/events/{category}/today` for category-specific results. Categories: `arts`, `comedy`, `music`, `film`, `fooddrink`, `lgbtq`, `recreation`, `sports`.

**Rich data available**: title, start/end datetime with timezone, venue with full address and lat/lng, ticket_info string, is_free boolean, sold_out boolean, buy_url, cover images at multiple resolutions, category, popularity score.

**File**: `backend/services/dothebay.py`

### Ticketmaster

**URL**: `https://app.ticketmaster.com/discovery/v2/events.json`

**Approach**: Standard REST API call with API key as query parameter.

**Key parameters**:
```
apikey=YOUR_KEY
keyword={search term}
city=San Francisco
stateCode=CA
countryCode=US
size=50
sort=date,asc
```

**Response**: Events in `_embedded.events[]`. Each event has: `name`, `dates.start.localDate`, `dates.start.localTime`, `_embedded.venues[0]` (name, address, city, lat/lng), `priceRanges[]` (min/max), `images[]` (multiple resolutions), `url`, `classifications[]` (segment, genre).

**Price**: `priceRanges` array is optional — many events don't include it. Fall back to "See listing".

**Images**: Multiple resolutions provided. Pick the one closest to 600px wide.

**Rate limit**: 5000 requests/day, 5 requests/second. No concern for MVP volume.

**File**: `backend/services/ticketmaster.py`

### Instagram (via Apify)

**Accounts**:
1. `@andrewtourssf`
2. `@valinthebay_` (handle TBC)
3. `@secret_sanfrancisco`
4. `@onlyinsf`
5. `@sfbaydiaries`
6. `@sfgirl.chronicle`
7. `@sfstandard`
8. `@sfbucketlist`

**Approach**: Use Apify's Instagram Post Scraper actor (`apify/instagram-post-scraper`) via the `apify-client` Python package. Fetch recent posts (last 30 days) from all 8 accounts. Extract caption, image URL, post date, and post URL.

**Keyword matching**: Match keyword against caption text (case-insensitive substring). Instagram posts are not structured events — many will be food reviews, city photos, etc. Only posts whose captions match the keyword are returned.

**Event data mapping**:
- `name`: First line of caption (truncated at 80 chars) or first sentence
- `summary`: Full caption text
- `start`: Post timestamp (this is when it was posted, not when an event occurs — a known limitation)
- `venue`: Not available (would require caption parsing)
- `image_url`: Post image URL from Apify response
- `url`: Instagram post permalink
- `source`: "Instagram"
- `price_range`: "See listing" (no structured price data)

**Known limitations**:
- Post date ≠ event date. A post about a Friday event might be posted Monday. No way to extract the actual event date without LLM parsing, which is out of scope for this sprint.
- No venue, address, or price data. These are free-text in captions.
- Some matched posts won't be events at all — a food photo captioned "comedy night vibes" would match a "comedy" search.

**Apify call pattern**:
```python
from apify_client import ApifyClient

client = ApifyClient(APIFY_TOKEN)
run = client.actor("apify/instagram-post-scraper").call(
    run_input={
        "usernames": ["andrewtourssf", "secret_sanfrancisco", ...],
        "resultsLimit": 30,  # per account
    }
)
items = client.dataset(run["defaultDatasetId"]).iterate_items()
```

**Cost**: ~$0.10-0.50 per run at 8 accounts × 30 posts. Free tier ($5/mo) easily covers daily use.

**Latency**: Apify runs take 30-60 seconds. This is too slow for a synchronous API call. Options:
1. **Background refresh**: Cron job fetches Instagram data every few hours, stores in memory or file. The API endpoint reads from the cache. — *Preferred, but caching is out of scope for this sprint.*
2. **Skip on timeout**: Call Apify with a 10-second timeout. If it doesn't return in time, skip Instagram results for that request. — *Simpler, but Instagram results would rarely appear.*
3. **Pre-fetch on startup**: Fetch Instagram data when the server starts. Stale after a few hours but always available. — *Good MVP compromise.*

**Decision**: Option 3 — pre-fetch on server startup. Store results in memory. Refresh manually by restarting the server. This keeps the architecture simple and avoids introducing caching infrastructure.

**File**: `backend/services/instagram.py`

---

## Unified Event Schema

All sources output this shape (unchanged from Sprint 1):

```json
{
  "id": "string",
  "name": "string",
  "summary": "string",
  "start": "ISO datetime string",
  "end": "ISO datetime string",
  "timezone": "string",
  "venue": "string",
  "address": "string",
  "neighborhood": "string",
  "latitude": number | null,
  "longitude": number | null,
  "image_url": "string",
  "is_free": boolean,
  "price_range": "string",
  "tickets": [],
  "url": "string",
  "source": "string"
}
```

Source values: `"Eventbrite"`, `"Lu.ma"`, `"19hz"`, `"Do The Bay"`, `"Ticketmaster"`, `"Instagram"`.

---

## Files Affected

### New Files

| File | Purpose |
|------|---------|
| `backend/services/nineteenhz.py` | 19hz HTML table scraper |
| `backend/services/dothebay.py` | Do The Bay JSON API client |
| `backend/services/ticketmaster.py` | Ticketmaster Discovery API client |
| `backend/services/instagram.py` | Apify Instagram Post Scraper client + startup pre-fetch |

### Modified Files

| File | Change |
|------|--------|
| `backend/main.py` | Import new services, add to `asyncio.gather()`, pre-fetch Instagram on startup |
| `backend/requirements.txt` | Add `beautifulsoup4`, `apify-client` |
| `Application/.env.example` | Add `TICKETMASTER_API_KEY`, `APIFY_TOKEN` |

### No Frontend Changes

The frontend already renders any event matching the unified schema. New sources will appear automatically with their `source` field displayed on each card.

---

## Environment Variables

```
EVENTBRITE_API_KEY=...          # existing
TICKETMASTER_API_KEY=...        # new — from developer.ticketmaster.com
APIFY_TOKEN=...                 # new — from apify.com
```

19hz and Do The Bay require no authentication.

---

## Error Handling

Same pattern as Sprint 1: each source is called via `asyncio.gather(return_exceptions=True)`. If a source fails, its results are skipped. The endpoint returns whatever succeeds. All six sources failing returns 502.

---

## Acceptance Criteria

1. Search returns events from all six sources (Eventbrite, Lu.ma, 19hz, Do The Bay, Ticketmaster, Instagram)
2. Each event shows the correct `source` label
3. 19hz events include: name, date/time, venue, price, genre tags, and link to original listing
4. Do The Bay events include: name, date/time, venue with address, price, image, and link
5. Ticketmaster events include: name, date/time, venue with address, price range, image, and link
6. Instagram results appear from pre-fetched data matching the keyword
7. Failure of any single source does not break the endpoint — remaining sources still return
8. No new secrets committed to git
