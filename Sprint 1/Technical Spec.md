# Sprint 1 — Technical Spec: Basic Event Search

**Created**: March 2026
**Status**: In Progress

---

## Goal

Prove the data pipeline works end-to-end. A user types a keyword, the backend calls Eventbrite, and the frontend displays matching SF events. No LLM, no semantic search, no auth.

---

## Scope

### In Scope

- Single text input for keyword search
- FastAPI backend endpoint that queries Eventbrite API
- Eventbrite search filtered to San Francisco
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
[React Frontend]  →  GET /api/events?q=comedy  →  [FastAPI Backend]  →  Eventbrite API
                  ←  JSON array of events       ←
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

**Styling:** Minimal. No design system yet. Basic CSS or Tailwind — enough to be readable, nothing fancy.

### Backend (FastAPI + Python)

**Files:**
- `main.py` — FastAPI app with a single endpoint
- `services/eventbrite.py` — Eventbrite API client
- `requirements.txt` — Dependencies

**Endpoint:**
```
GET /api/events?q={keyword}
```

**Response shape:**
```json
[
  {
    "id": "eventbrite-123",
    "name": "Comedy Night at Cobb's",
    "start": "2026-03-29T20:00:00",
    "end": "2026-03-29T22:00:00",
    "venue": "Cobb's Comedy Club",
    "address": "915 Columbus Ave, San Francisco, CA",
    "price": "Free" | "$25.00",
    "url": "https://eventbrite.com/e/123",
    "source": "Eventbrite"
  }
]
```

**Eventbrite integration:**
- Uses Eventbrite v3 API: `GET /v3/events/search/`
- Query params: `q={keyword}`, `location.address=San Francisco, CA`, `location.within=10mi`
- API key stored in `.env` (backend only), never committed
- Parse response to extract: event name, start/end time, venue, ticket price (free or minimum price), URL
- Return top 20 results, sorted by date (soonest first)

**Error handling:**
- Eventbrite API down or rate limited → return 502 with message
- No results → return empty array (200)
- Missing API key → fail fast on startup with clear error

---

## Project Structure

```
tonight/
├── Application/
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
│       │   └── eventbrite.py
│       ├── requirements.txt
│       └── .env  (git-ignored)
```

---

## Environment & Config

- **Eventbrite API key**: Stored in `backend/.env` as `EVENTBRITE_API_KEY`
- **CORS**: Backend allows requests from `http://localhost:5173` (Vite dev server)
- **Ports**: Frontend on 5173 (Vite default), backend on 8000 (Uvicorn default)

---

## Dev Setup

```bash
# Backend
cd Application/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Add EVENTBRITE_API_KEY to .env
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
