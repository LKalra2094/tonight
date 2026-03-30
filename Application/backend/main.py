import asyncio
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from services.eventbrite import search_events as eventbrite_search
from services.luma import search_events as luma_search

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

EVENTBRITE_API_KEY = os.getenv("EVENTBRITE_API_KEY")
if not EVENTBRITE_API_KEY:
    raise RuntimeError("EVENTBRITE_API_KEY not set in .env")

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
        eb_results, luma_results = await asyncio.gather(
            eventbrite_search(EVENTBRITE_API_KEY, q),
            luma_search(q),
            return_exceptions=True,
        )

        events = []
        if isinstance(eb_results, list):
            events.extend(eb_results)
        if isinstance(luma_results, list):
            events.extend(luma_results)

        events.sort(key=lambda e: e["start"])
        return events

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Could not fetch events",
        )
