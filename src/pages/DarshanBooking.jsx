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

export default function DarshanBooking() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const today = getTodayDate();

  const [form, setForm] = useState({
    temple: params.get("temple") || "",
    date: "",
    slot: "Morning",
    persons: 1,
  });
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    if (form.date < today) {
      setError("Please select today's date or a future date.");
      return;
    }

    const numPersons = Number(form.persons);
    if (!numPersons || numPersons < 1 || numPersons > 5) {
      setError("Booking limit is up to 5 persons.");
      return;
    }

    const t = temples.find((x) => x.id === form.temple);
    navigate("/user-details", {
      state: {
        type: "Darshan",
        temple: t?.name || "",
        data: { ...form, persons: numPersons },
      },
    });
  };

  return (
    <section className="section page narrow">
      <div className="section-heading">
        <p className="eyebrow">DARSHAN</p>
        <h1>Book Darshan</h1>
        <p>
          Your booking is saved to MySQL through the backend after you enter your contact details.
        </p>
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
          Date
          <input
            required
            type="date"
            min={today}
            value={form.date}
            onChange={(e) => setForm({ ...form, date: e.target.value })}
          />
        </label>

        <label>
          Slot
          <select
            value={form.slot}
            onChange={(e) => setForm({ ...form, slot: e.target.value })}
          >
            <option>Morning</option>
            <option>Afternoon</option>
            <option>Evening</option>
          </select>
        </label>

        <label>
          Number of Persons (Max 5)
          <input
            required
            min="1"
            max="5"
            type="number"
            value={form.persons}
            onChange={(e) => setForm({ ...form, persons: e.target.value })}
          />
        </label>

        {error && <div className="error">{error}</div>}

        <button className="btn primary">Continue</button>
      </form>
    </section>
  );
}
