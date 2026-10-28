import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { temples } from "../data/temples";

const getTodayDate = () => {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

export default function Bhojan() {
  const navigate = useNavigate();
  const today = getTodayDate();

  const [form, setForm] = useState({
    temple: "",
    date: "",
    persons: 1,
    meal: "Lunch",
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
        type: "Bhojan",
        temple: t?.name || "",
        data: { ...form, persons: numPersons },
      },
    });
  };

  return (
    <section className="section page narrow">
      <div className="section-heading">
        <p className="eyebrow">BHOJAN</p>
        <h1>Temple Bhojan</h1>
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
              <option key={t.id} value={t.id}>
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
          Meal
          <select
            value={form.meal}
            onChange={(e) => setForm({ ...form, meal: e.target.value })}
          >
            <option>Breakfast</option>
            <option>Lunch</option>
            <option>Dinner</option>
          </select>
        </label>

        <label>
          Persons (Max 5)
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
