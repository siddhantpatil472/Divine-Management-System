import { useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { temples } from "../data/temples";

const poojas = [
  "Ganapati Pooja",
  "Abhishek",
  "Maha Aarti",
  "Special Pooja",
  "Rudrabhishek",
];

const getTodayDate = () => {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

export default function Pooja() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const today = getTodayDate();

  const [form, setForm] = useState({
    temple: params.get("temple") || "",
    pooja: poojas[0],
    date: "",
  });
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    if (form.date < today) {
      setError("Please select today's date or a future date.");
      return;
    }

    const t = temples.find((x) => x.id === form.temple);
    navigate("/user-details", {
      state: {
        type: "Pooja",
        temple: t?.name || "",
        data: form,
      },
    });
  };

  return (
    <section className="section page narrow">
      <div className="section-heading">
        <p className="eyebrow">POOJA</p>
        <h1>Book a Pooja</h1>
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
          Pooja
          <select
            value={form.pooja}
            onChange={(e) => setForm({ ...form, pooja: e.target.value })}
          >
            {poojas.map((p) => (
              <option key={p}>{p}</option>
            ))}
          </select>
        </label>

        <label>
          Preferred Date
          <input
            required
            type="date"
            min={today}
            value={form.date}
            onChange={(e) => setForm({ ...form, date: e.target.value })}
          />
        </label>

        {error && <div className="error">{error}</div>}

        <button className="btn primary">Continue</button>
      </form>
    </section>
  );
}
