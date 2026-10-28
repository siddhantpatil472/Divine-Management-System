
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";

export default function Events() {
  const [events, setEvents] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    const loadEvents = async () => {
      try {
        const result = await api.events();
        const list = Array.isArray(result)
          ? result
          : Array.isArray(result.events)
          ? result.events
          : [];

        if (active) {
          setEvents(
            list.filter(
              (event) =>
                String(event.status || "OPEN").toUpperCase() === "OPEN"
            )
          );
          setError("");
        }
      } catch (err) {
        if (active) setError(err.message);
      }
    };

    loadEvents();
    const timer = setInterval(loadEvents, 5000);

    return () => {
      active = false;
      clearInterval(timer);
    };
  }, []);

  return (
    <section className="section page">
      <div className="section-heading">
        <p className="eyebrow">EVENTS</p>
        <h1>Upcoming Temple Events</h1>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="event-grid">
        {events.length > 0 ? (
          events.map((event) => (
            <article className="event-card" key={event.id}>
              <span className="event-date">
                {event.event_date || event.date || "-"}
              </span>
              <h3>
                {event.title || event.name || event.event_name}
              </h3>
              <p>{event.temple_name || "Temple"}</p>
              <p>{event.event_time || event.time || "-"}</p>

              {event.description && <p>{event.description}</p>}

              <Link
                className="text-link"
                to="/user-details"
                state={{
                  type: "Event",
                  temple: event.temple_name,
                  data: {
                    ...event,
                    temple: event.temple_id,
                  },
                }}
              >
                Register →
              </Link>
            </article>
          ))
        ) : (
          !error && <p>No upcoming events available.</p>
        )}
      </div>
    </section>
  );
}