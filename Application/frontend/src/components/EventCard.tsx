interface Event {
  id: string;
  name: string;
  start: string;
  end: string;
  venue: string;
  address: string;
  price: string;
  url: string;
  source: string;
}

interface EventCardProps {
  event: Event;
}

export default function EventCard({ event }: EventCardProps) {
  const formatDate = (dateStr: string) => {
    if (!dateStr) return "Date TBD";
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  };

  return (
    <div className="event-card">
      <h3>{event.name}</h3>
      <p className="event-date">{formatDate(event.start)}</p>
      <p className="event-venue">{event.venue}</p>
      <p className="event-address">{event.address}</p>
      <p className="event-price">{event.price}</p>
      <a href={event.url} target="_blank" rel="noopener noreferrer">
        View on {event.source} →
      </a>
    </div>
  );
}

export type { Event };
