import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from httpx import HTTPStatusError, RequestError

from services.eventbrite import search_events

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
        events = await search_events(EVENTBRITE_API_KEY, q)
        return events
    except HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Eventbrite API error: {e.response.status_code}",
        )
    except RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not reach Eventbrite API",
        )
