import { useState } from "react";
import SearchBar from "./components/SearchBar";
import EventList from "./components/EventList";
import type { Event } from "./components/EventCard";
import "./App.css";

const API_BASE = "http://localhost:8000";

function App() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <div className="app">
      <h1>Tonight</h1>
      <p className="subtitle">Search SF events</p>
      <SearchBar onSearch={handleSearch} loading={loading} />
      {error && <p className="error">{error}</p>}
      <EventList events={events} searched={searched} />
    </div>
  );
}

export default App;
