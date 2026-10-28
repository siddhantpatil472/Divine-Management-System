
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";

export default function TrusteeDashboard() {
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [events, setEvents] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [closingId, setClosingId] = useState(null);

  const [form, setForm] = useState({
    title: "",
    event_date: "",
    event_time: "",
    description: ""
  });

  const info = JSON.parse(
    localStorage.getItem("divine_trustee_info") || "null"
  );

  async function load() {
    setError("");

    try {
      const dashboard = await api.trusteeDashboard();
      setData(dashboard);

      const result = await api.trusteeEvents();

      const list = Array.isArray(result)
        ? result
        : Array.isArray(result.events)
        ? result.events
        : [];

      setEvents(list);
    } catch (err) {
      setError(err.message || "Unable to load dashboard.");

      if (
        /login|session|token|unauthorized/i.test(err.message || "")
      ) {
        localStorage.removeItem("divine_trustee_token");
        navigate("/trustee/login");
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function addEvent(e) {
    e.preventDefault();
    setSaving(true);
    setError("");

    try {
      await api.addTrusteeEvent(form);

      setForm({
        title: "",
        event_date: "",
        event_time: "",
        description: ""
      });

      setShowForm(false);
      await load();
    } catch (err) {
      setError(err.message || "Unable to add event.");
    } finally {
      setSaving(false);
    }
  }

  async function closeEvent(id) {
    if (!window.confirm("Are you sure you want to close this event?")) {
      return;
    }

    setClosingId(id);
    setError("");

    try {
      await api.closeTrusteeEvent(id);
      await load();
    } catch (err) {
      setError(err.message || "Unable to close event.");
    } finally {
      setClosingId(null);
    }
  }

  async function confirmBooking(id) {
    try {
      await api.confirmBooking(id);
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function confirmDonation(id) {
    try {
      await api.confirmDonation(id);
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  function logout() {
    localStorage.removeItem("divine_trustee_token");
    localStorage.removeItem("divine_trustee_info");
    navigate("/trustee/login");
  }

  if (loading) {
    return (
      <section className="section page">
        <p>Loading trustee dashboard...</p>
      </section>
    );
  }

  return (
    <section className="section page trustee-page">
      <div className="trustee-head">
        <div>
          <p className="eyebrow">TRUSTEE DASHBOARD</p>
          <h1>{info?.temple_name || "Temple"} Trustee Dashboard</h1>
          <p>
            Logged in as <strong>{info?.display_name || "Trustee"}</strong>.
            {" "}You can only manage records belonging to this temple.
          </p>
        </div>

        <button className="btn secondary" onClick={logout}>
          Logout
        </button>
      </div>

      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}

      {/* DASHBOARD STATISTICS */}
      <div className="stats-grid">
        <div className="stat-card">
          <span>Pending Bookings</span>
          <strong>{data?.stats?.pending_bookings || 0}</strong>
        </div>

        <div className="stat-card">
          <span>Confirmed Bookings</span>
          <strong>{data?.stats?.confirmed_bookings || 0}</strong>
        </div>

        <div className="stat-card">
          <span>Pending Donations</span>
          <strong>{data?.stats?.pending_donations || 0}</strong>
        </div>

        <div className="stat-card">
          <span>Confirmed Donations</span>
          <strong>{data?.stats?.confirmed_donations || 0}</strong>
        </div>
      </div>

      {/* EVENTS SECTION */}
      <div className="dashboard-section">
        <div className="section-heading">
          <p className="eyebrow">EVENTS</p>
          <h2>Temple Events</h2>
          <p>Manage upcoming events for your temple.</p>

          <button
            type="button"
            className="btn"
            onClick={() => setShowForm(previous => !previous)}
          >
            {showForm ? "Cancel" : "+ Add New Event"}
          </button>
        </div>

        {showForm && (
          <form className="event-form" onSubmit={addEvent}>
            <label>
              Event Name
              <input
                type="text"
                value={form.title}
                onChange={e =>
                  setForm({ ...form, title: e.target.value })
                }
                placeholder="e.g. Ganesh Chaturthi"
                required
              />
            </label>

            <label>
              Event Date
              <input
                type="date"
                min={new Date().toLocaleDateString('en-CA')}
                value={form.event_date}
                onChange={e =>
                  setForm({ ...form, event_date: e.target.value })
                }
                required
              />
            </label>

            <label>
              Event Time
              <input
                type="time"
                value={form.event_time}
                onChange={e =>
                  setForm({ ...form, event_time: e.target.value })
                }
                required
              />
            </label>

            <label>
              Description
              <textarea
                value={form.description}
                onChange={e =>
                  setForm({ ...form, description: e.target.value })
                }
                placeholder="Enter event details"
                rows={3}
              />
            </label>

            <button className="btn" type="submit" disabled={saving}>
              {saving ? "Saving Event..." : "Save Event"}
            </button>
          </form>
        )}

        <div className="event-list">
          {events.length === 0 ? (
            <p>No events found for this temple.</p>
          ) : (
            events.map(event => {
              const status = String(event.status || "OPEN").toUpperCase();
              const isOpen = status === "OPEN";

              return (
                <article className="event-card" key={event.id}>
                  <div className="event-details">
                    <h3>{event.title || event.event_name || "Temple Event"}</h3>

                    <p>
                      <strong>Date:</strong>{" "}
                      {event.event_date || event.date || "-"}
                    </p>

                    <p>
                      <strong>Time:</strong>{" "}
                      {event.event_time || "-"}
                    </p>

                    <p>
                      <strong>Status:</strong>{" "}
                      <span className={`status ${status.toLowerCase()}`}>
                        {status}
                      </span>
                    </p>

                    {event.description && (
                      <p>{event.description}</p>
                    )}
                  </div>

                  {/* Always show the button */}
                  <button
                    type="button"
                    className="btn secondary"
                    disabled={!isOpen || closingId === event.id}
                    onClick={() => closeEvent(event.id)}
                  >
                    {closingId === event.id
                      ? "Closing..."
                      : isOpen
                      ? "Close Event"
                      : "Event Closed"}
                  </button>
                </article>
              );
            })
          )}
        </div>

        <button
          type="button"
          className="btn secondary"
          onClick={load}
        >
          Refresh Events
        </button>
      </div>

      {/* BOOKINGS SECTION */}
      <div className="dashboard-section">
        <div className="section-heading">
          <p className="eyebrow">BOOKINGS</p>
          <h2>Booking Requests</h2>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>User</th>
                <th>Type</th>
                <th>Date</th>
                <th>Payment</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {data?.bookings?.length ? (
                data.bookings.map(b => (
                  <tr key={b.id}>
                    <td>#{b.id}</td>
                    <td>
                      <strong>{b.name}</strong>
                      <br />{b.phone}
                      <br />{b.email}
                    </td>
                    <td>{b.booking_type}</td>
                    <td>{b.date || b.checkin || "-"}</td>
                    <td>
                      {b.transaction_id ? (
                        <>
                          <strong>₹{b.payment_amount}</strong>
                          <br />{b.payment_method}
                          <br />
                          <small>{b.transaction_id}</small>
                        </>
                      ) : (
                        "No payment record"
                      )}
                    </td>
                    <td>
                      <span className={`status ${String(b.status).toLowerCase()}`}>
                        {b.status}
                      </span>
                    </td>
                    <td>
                      {b.status === "PENDING" ? (
                        <button
                          className="btn small"
                          onClick={() => confirmBooking(b.id)}
                        >
                          Confirm
                        </button>
                      ) : (
                        <span>{b.ticket_no}</span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7">No bookings for this temple.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* DONATIONS SECTION */}
      <div className="dashboard-section">
        <div className="section-heading">
          <p className="eyebrow">DONATIONS</p>
          <h2>Donation Requests</h2>
        </div>

        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Donor</th>
                <th>Amount</th>
                <th>Purpose</th>
                <th>Payment</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {data?.donations?.length ? (
                data.donations.map(d => (
                  <tr key={d.id}>
                    <td>#{d.id}</td>
                    <td>
                      <strong>{d.name}</strong>
                      <br />{d.phone}
                      <br />{d.email}
                    </td>
                    <td>₹{d.amount}</td>
                    <td>{d.purpose}</td>
                    <td>
                      {d.transaction_id ? (
                        <>
                          <strong>{d.payment_method}</strong>
                          <br />
                          <small>{d.transaction_id}</small>
                        </>
                      ) : (
                        "No payment record"
                      )}
                    </td>
                    <td>
                      <span className={`status ${String(d.status).toLowerCase()}`}>
                        {d.status}
                      </span>
                    </td>
                    <td>
                      {d.status === "PENDING" ? (
                        <button
                          className="btn small"
                          onClick={() => confirmDonation(d.id)}
                        >
                          Confirm
                        </button>
                      ) : (
                        <span>{d.receipt_no}</span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7">No donations for this temple.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}