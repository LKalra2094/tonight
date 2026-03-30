interface Ticket {
  name: string;
  price: string;
  free: boolean;
  status: string;
}

interface Event {
  id: string;
  name: string;
  description: string;
  summary: string;
  start: string;
  end: string;
  timezone: string;
  venue: string;
  address: string;
  latitude: string | null;
  longitude: string | null;
  image_url: string;
  is_free: boolean;
  is_online: boolean;
  price_range: string;
  tickets: Ticket[];
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
    });
  };

  const formatTime = (dateStr: string) => {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    return date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
    });
  };

  return (
    <a href={event.url} target="_blank" rel="noopener noreferrer" className="event-card">
      {event.image_url && (
        <img
          className="event-image"
          src={event.image_url}
          alt={event.name}
        />
      )}
      <div className="event-content">
        <h3 className="event-name">{event.name}</h3>
        <p className="event-date">
          {formatDate(event.start)} · {formatTime(event.start)}
        </p>
        <p className="event-venue">{event.venue}</p>
        <p className="event-price">{event.price_range}</p>
      </div>
    </a>
  );
}

export type { Event };
