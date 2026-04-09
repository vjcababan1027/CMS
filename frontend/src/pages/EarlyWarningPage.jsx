import { useEffect, useState } from "react";
import { riskPredictionsService } from "../services/crudService";

const emptyForm = {
  student_id: "",
  class_id: "",
  risk_score: "",
  risk_level: "moderate",
  features_used: "",
  model_version: "v1"
};

export default function EarlyWarningPage() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await riskPredictionsService.list();
      setItems(data);
    } catch (e) {
      setError(e?.response?.data?.detail || "Failed to load risk predictions");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await riskPredictionsService.create({
        ...form,
        student_id: Number(form.student_id),
        class_id: Number(form.class_id),
        risk_score: Number(form.risk_score)
      });
      setForm(emptyForm);
      await load();
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to create risk prediction");
    }
  }

  async function handleDelete(id) {
    try {
      await riskPredictionsService.remove(id);
      await load();
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to delete risk prediction");
    }
  }

  return (
    <section className="panel">
      <h2 style={{ fontSize: 30, fontWeight: 800, color: "var(--primary)" }}>Early Warning System</h2>
      <p className="muted">Manage at-risk student predictions and interventions.</p>

      {error && <p className="error-text">{typeof error === "string" ? error : JSON.stringify(error)}</p>}

      <form className="form-grid" onSubmit={handleSubmit}>
        <label>
          Student ID
          <input
            required
            value={form.student_id}
            onChange={(e) => setForm({ ...form, student_id: e.target.value })}
          />
        </label>
        <label>
          Class ID
          <input
            required
            value={form.class_id}
            onChange={(e) => setForm({ ...form, class_id: e.target.value })}
          />
        </label>
        <label>
          Risk Score (0-1)
          <input
            required
            type="number"
            min="0"
            max="1"
            step="0.01"
            value={form.risk_score}
            onChange={(e) => setForm({ ...form, risk_score: e.target.value })}
          />
        </label>
        <label>
          Risk Level
          <select
            value={form.risk_level}
            onChange={(e) => setForm({ ...form, risk_level: e.target.value })}
          >
            <option value="low">Low</option>
            <option value="moderate">Moderate</option>
            <option value="high">High</option>
          </select>
        </label>
        <label>
          Features Used
          <input
            value={form.features_used}
            onChange={(e) => setForm({ ...form, features_used: e.target.value })}
          />
        </label>
        <label>
          Model Version
          <input
            value={form.model_version}
            onChange={(e) => setForm({ ...form, model_version: e.target.value })}
          />
        </label>
        <button className="btn primary-gradient" type="submit">
          Add Prediction
        </button>
      </form>

      <div className="table-wrap mt-16">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Student</th>
              <th>Class</th>
              <th>Risk Score</th>
              <th>Risk Level</th>
              <th>Model</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {!loading &&
              items.map((row) => (
                <tr key={row.id}>
                  <td>{row.id}</td>
                  <td>{row.student_id}</td>
                  <td>{row.class_id}</td>
                  <td>{row.risk_score}</td>
                  <td>{row.risk_level}</td>
                  <td>{row.model_version || "-"}</td>
                  <td>
                    <button className="btn danger" onClick={() => handleDelete(row.id)}>
                      Deactivate
                    </button>
                  </td>
                </tr>
              ))}
            {!loading && items.length === 0 && (
              <tr>
                <td colSpan={7} className="muted">
                  No risk predictions yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
