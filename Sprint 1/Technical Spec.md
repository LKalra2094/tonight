# Sprint 1 — Technical Spec: Basic Event Search

**Created**: March 2026
**Status**: Closed

---

## Goal

Prove the data pipeline works end-to-end. A user types a keyword, the backend finds matching SF events on Eventbrite, and the frontend displays them. No LLM, no semantic search, no auth.

---

## Why Not Eventbrite's API Directly?

Eventbrite deprecated their public event search endpoint (`/v3/events/search/`) in December 2019. The only remaining endpoints require a known event ID or organization ID — you can't search by keyword + city.

**What still works:**
- `GET /v3/events/{id}/` — fetch a single event by ID (with venue, ticket info)

**What's gone:**
- `GET /v3/events/search/` — keyword + location search (returns 404)

### Our workaround: SerpApi + Eventbrite API

1. **SerpApi** — search Google for `site:eventbrite.com {keyword} san francisco` → returns Eventbrite URLs
2. **Extract event IDs** from the URLs (the number in the path, e.g. `1979836428052`)
3. **Eventbrite API** — `GET /v3/events/{id}/?expand=venue,ticket_availability` → structured event data

This gives us keyword search (via Google) and structured data (via Eventbrite's working endpoint). SerpApi's free tier is 100 searches/month — sufficient for a personal project.

---

## Scope

### In Scope

- Single text input for keyword search
- FastAPI backend that searches via SerpApi and enriches via Eventbrite API
- Results filtered to San Francisco Eventbrite listings
- Frontend displays results as a simple list
- Each result shows: event name, date/time, venue name, price (free or paid), and link to Eventbrite listing

### Out of Scope

- User accounts, auth, onboarding
- LLM parsing or intent extraction
- Multiple API sources (Yelp, Google Places, scrapers)
- Plan generation, scoring, or ranking
- Budget, time, or preference filtering
- Map, photos, or timeline views

---

## Architecture

```
[React Frontend]
        │
        │  GET /api/events?q=comedy
        ▼
[FastAPI Backend]
        │
        ├──  1. SerpApi (Google search: site:eventbrite.com {keyword} san francisco)
        │       → returns list of Eventbrite URLs
        │
        ├──  2. Extract event IDs from URLs
        │
        └──  3. Eventbrite API (GET /v3/events/{id}/?expand=venue,ticket_availability)
                → returns structured event data per ID
```

### Frontend (Vite + React)

**Files:**
- `src/App.tsx` — Single-page app with search input and results list
- `src/components/SearchBar.tsx` — Text input + submit button
- `src/components/EventList.tsx` — Renders list of event cards
- `src/components/EventCard.tsx` — Single event: name, date, venue, price, link

**Behavior:**
- User types keyword and hits Enter or clicks Search
- Frontend calls `GET /api/events?q={keyword}`
- Displays loading state while waiting
- Renders results as a vertical list
- Shows "No events found" if empty response

**Styling:** Minimal. Basic CSS — enough to be readable, nothing fancy.

### Backend (FastAPI + Python)

**Files:**
- `main.py` — FastAPI app with a single endpoint
- `services/serpapi.py` — SerpApi client for Google search
- `services/eventbrite.py` — Eventbrite API client for event details
- `requirements.txt` — Dependencies

**Endpoint:**
```
GET /api/events?q={keyword}
```

**Response shape:**
```json
[
  {
    "id": "1979836428052",
    "name": "Comedy Night at Cobb's",
    "start": "2026-03-29T20:00:00",
    "end": "2026-03-29T22:00:00",
    "venue": "Cobb's Comedy Club",
    "address": "915 Columbus Ave, San Francisco, CA",
    "price": "Free" | "$25.00",
    "url": "https://eventbrite.com/e/comedy-night-tickets-1979836428052",
    "source": "Eventbrite"
  }
]
```

**SerpApi integration:**
- Uses SerpApi Google Search: `GET https://serpapi.com/search?engine=google&q=site:eventbrite.com+{keyword}+san+francisco`
- Parses organic results for Eventbrite event URLs
- Extracts event IDs from URL paths using regex

**Eventbrite integration:**
- Uses Eventbrite v3 API: `GET /v3/events/{id}/?expand=venue,ticket_availability`
- API key passed as Bearer token
- Extracts: event name, start/end time, venue name, address, ticket price, URL
- Calls are made concurrently for all extracted IDs

**Error handling:**
- SerpApi or Eventbrite down → return 502 with message
- No results → return empty array (200)
- Missing API keys → fail fast on startup with clear error
- Individual event fetch fails → skip that event, return the rest

---

## Project Structure

```
tonight/
├── Application/
│   ├── .env              (git-ignored, all API keys)
│   ├── .env.example
│   ├── frontend/
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── index.html
│   │   └── src/
│   │       ├── App.tsx
│   │       └── components/
│   │           ├── SearchBar.tsx
│   │           ├── EventList.tsx
│   │           └── EventCard.tsx
│   └── backend/
│       ├── main.py
│       ├── services/
│       │   ├── serpapi.py
│       │   └── eventbrite.py
│       └── requirements.txt
```

---

## Environment & Config

- **SerpApi key**: Stored in `Application/.env` as `SERPAPI_API_KEY`
- **Eventbrite API key**: Stored in `Application/.env` as `EVENTBRITE_API_KEY`
- **CORS**: Backend allows requests from `http://localhost:5173` (Vite dev server)
- **Ports**: Frontend on 5173 (Vite default), backend on 8000 (Uvicorn default)

---

## Dev Setup

```bash
# Backend
cd Application/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Add SERPAPI_API_KEY and EVENTBRITE_API_KEY to Application/.env
uvicorn main:app --reload

# Frontend
cd Application/frontend
npm install
npm run dev
```

---

## Acceptance Criteria

1. User can type a keyword and see SF events from Eventbrite
2. Each event shows name, date/time, venue, price, and a working link to the Eventbrite listing
3. Empty searches show "No events found"
4. API errors show a user-facing error message, not a blank screen
5. No secrets committed to git

---

## Limitations

- **SerpApi free tier**: 100 searches/month. Sufficient for personal use, not for scale.
- **Two-hop latency**: Each search requires a SerpApi call + multiple Eventbrite API calls. Slower than a single API would be.
- **Google result quality**: SerpApi returns whatever Google indexes. Some results may be expired, sold out, or outside SF.
- **No Eventbrite search API**: This workaround exists because Eventbrite removed their public search endpoint in 2019. If they restore it or offer a partner program, we should switch back.
