import React, { useEffect, useState } from "react";
import api from "../api";

export default function LearningPortals() {
  const [categories, setCategories] = useState(null);

  useEffect(() => {
    api.getLearningPortals().then((d) => setCategories(d.categories));
  }, []);

  if (!categories) return <div><h2>Learning Portals</h2><p className="muted">Loading...</p></div>;

  return (
    <div>
      <h2>Learning Portals</h2>
      <p className="muted">Curated MOOC platforms, coding practice sites, certification providers, and reference docs.</p>

      {Object.entries(categories).map(([category, items]) => (
        <div className="card" key={category}>
          <h3>{category}</h3>
          {items.map((item) => (
            <div key={item.name} style={{ marginBottom: 12 }}>
              <a href={item.url} target="_blank" rel="noreferrer" style={{ fontWeight: 600, color: "#1f4e79" }}>
                {item.name}
              </a>
              <p className="muted" style={{ margin: "2px 0 0" }}>{item.description}</p>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
