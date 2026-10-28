
import { Link, useParams } from "react-router-dom";
import { temples } from "../data/temples";

export default function TempleDetails() {
  const { id } = useParams();
  const t = temples.find((x) => x.id === id);

  if (!t) {
    return (
      <section className="section page">
        <h1>Temple not found</h1>
        <Link to="/temples">Back to Temples</Link>
      </section>
    );
  }

  return (
    <section className="section page">
      <div className="details-card">
        <img
          className="details-image"
          src={t.image}
          alt={t.name}
        />

        <div className="details-content">
          <p className="eyebrow">TEMPLE DETAILS</p>

          <h1>{t.name}</h1>

          <p>
            <strong>Location:</strong> {t.location}
          </p>

          <p>
            <strong>Deity:</strong> {t.deity}
          </p>

          <h3>About the Temple</h3>
          <p>{t.history}</p>
        </div>
      </div>
    </section>
  );
}