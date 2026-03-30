import EventCard from "./EventCard";
import type { Event } from "./EventCard";

interface EventListProps {
  events: Event[];
  searched: boolean;
}

export default function EventList({ events, searched }: EventListProps) {
  if (!searched) return null;

  if (events.length === 0) {
    return <p className="no-results">No events found. Try a different keyword.</p>;
  }

  return (
    <div className="event-list">
      {events.map((event) => (
        <EventCard key={event.id} event={event} />
      ))}
    </div>
  );
}
