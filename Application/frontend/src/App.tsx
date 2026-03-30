import { useState } from "react";
import SearchBar from "./components/SearchBar";
import PriceFilter from "./components/PriceFilter";
import EventList from "./components/EventList";
import type { Event } from "./components/EventCard";
import "./App.css";

const API_BASE = "http://localhost:8000";

function parseMaxPrice(priceRange: string): number | null {
  if (priceRange === "Free") return 0;
  if (priceRange === "See listing" || priceRange === "Invite only") return null;
  const matches = priceRange.match(/\d+/g);
  if (!matches) return null;
  return Math.max(...matches.map(Number));
}

function App() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [maxPrice, setMaxPrice] = useState("");
  const [hideInviteOnly, setHideInviteOnly] = useState(false);

  const handleSearch = async (keyword: string) => {
    setLoading(true);
    setError(null);
    setSearched(true);

    try {
      const response = await fetch(
        `${API_BASE}/api/events?q=${encodeURIComponent(keyword)}`
      );
      if (!response.ok) {
        const data = await response.json().catch(() => null);
        throw new Error(data?.detail || `Error: ${response.status}`);
      }
      const data = await response.json();
      setEvents(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong"
      );
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredEvents = events.filter((event) => {
    if (hideInviteOnly && event.price_range === "Invite only") return false;
    if (maxPrice !== "") {
      const price = parseMaxPrice(event.price_range);
      if (price !== null && price > Number(maxPrice)) return false;
    }
    return true;
  });

  return (
    <div className="app">
      <div className="header">
        <div>
          <h1>Tonight</h1>
          <p className="subtitle">Search SF events</p>
        </div>
        <div className="filters">
          <label className="invite-filter">
            <input
              type="checkbox"
              checked={hideInviteOnly}
              onChange={(e) => setHideInviteOnly(e.target.checked)}
            />
            Hide invite only
          </label>
          <PriceFilter value={maxPrice} onChange={setMaxPrice} />
        </div>
      </div>
      <SearchBar onSearch={handleSearch} loading={loading} />
      {error && <p className="error">{error}</p>}
      <EventList events={filteredEvents} searched={searched} />
    </div>
  );
}

export default App;
