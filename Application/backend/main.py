import asyncio
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from services.eventbrite import search_events as eventbrite_search
from services.luma import search_events as luma_search
from services.nineteenhz import search_events as nineteenhz_search
from services.dothebay import search_events as dothebay_search
from services.ticketmaster import search_events as ticketmaster_search
from services.instagram import search_events as instagram_search

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

EVENTBRITE_API_KEY = os.getenv("EVENTBRITE_API_KEY")
if not EVENTBRITE_API_KEY:
    raise RuntimeError("EVENTBRITE_API_KEY not set in .env")

TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY", "")
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "")

app = FastAPI(title="Tonight API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/events")
async def get_events(q: str = Query(..., min_length=1, description="Search keyword")):
    try:
        tasks = [
            eventbrite_search(EVENTBRITE_API_KEY, q),
            luma_search(q),
            nineteenhz_search(q),
            dothebay_search(q),
        ]

        # Only include sources that have API keys configured
        if TICKETMASTER_API_KEY:
            tasks.append(ticketmaster_search(TICKETMASTER_API_KEY, q))
        if APIFY_TOKEN:
            tasks.append(instagram_search(APIFY_TOKEN, q))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        events = []
        for result in results:
            if isinstance(result, list):
                events.extend(result)

        if not events and all(isinstance(r, Exception) for r in results):
            raise HTTPException(
                status_code=502,
                detail="Could not fetch events from any source",
            )

        events.sort(key=lambda e: e.get("start", ""))
        return events

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Could not fetch events",
        )
