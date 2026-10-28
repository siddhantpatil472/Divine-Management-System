import { useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { temples } from "../data/temples";

const getTodayDate = () => {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

export default function RoomBooking() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const today = getTodayDate();

  const [form, setForm] = useState({
    temple: params.get("temple") || "",
    checkin: "",
    checkout: "",
    rooms: 1,
  });
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    if (form.checkin < today) {
      setError("Check-in date cannot be in the past.");
      return;
    }
    if (form.checkout <= form.checkin) {
      setError("Check-out date must be after check-in date.");
      return;
    }

    const t = temples.find((x) => x.id === form.temple);
    navigate("/user-details", {
      state: {
        type: "Room Booking",
        temple: t?.name || "",
        data: form,
      },
    });
  };

  return (
    <section className="section page narrow">
      <div className="section-heading">
        <p className="eyebrow">ACCOMMODATION</p>
        <h1>Room Booking</h1>
        <p>Room availability is checked and stored by the backend.</p>
      </div>

      <form className="form-card" onSubmit={handleSubmit}>
        <label>
          Temple
          <select
            required
            value={form.temple}
            onChange={(e) => setForm({ ...form, temple: e.target.value })}
          >
            <option value="">Select Temple</option>
            {temples.map((t) => (
              <option value={t.id} key={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Check-in
          <input
            required
            type="date"
            min={today}
            value={form.checkin}
            onChange={(e) => setForm({ ...form, checkin: e.target.value })}
          />
        </label>

        <label>
          Check-out
          <input
            required
            type="date"
            min={form.checkin || today}
            value={form.checkout}
            onChange={(e) => setForm({ ...form, checkout: e.target.value })}
          />
        </label>

        <label>
          Number of Rooms
          <input
            required
            min="1"
            max="50"
            type="number"
            value={form.rooms}
            onChange={(e) => setForm({ ...form, rooms: e.target.value })}
          />
        </label>

        {error && <div className="error">{error}</div>}

        <button className="btn primary">Continue</button>
      </form>
    </section>
  );
}
