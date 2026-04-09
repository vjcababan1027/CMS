import { useEffect, useState } from "react";
import { parentReportingService } from "../services/crudService";

const emptyForm = {
  student_id: "",
  parent_email: "",
  period: "prelim",
  attendance_summary: "",
  risk_level: "moderate",
  teacher_remarks: "",
  status: "pending"
};

function formatError(err, fallback) {
  const detail = err?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => d?.msg || JSON.stringify(d)).join("; ");
  }
  return detail || fallback;
}

export default function ParentReportingPage() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [dispatchResult, setDispatchResult] = useState(null);

  async function load() {
    setError("");
    try {
      const data = await parentReportingService.list();
      setItems(data);
    } catch (e) {
      setError(formatError(e, "Failed to load parent reporting logs"));
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      await parentReportingService.create({
        ...form,
        student_id: Number(form.student_id)
      });
      setForm(emptyForm);
      await load();
    } catch (err) {
      setError(formatError(err, "Failed to create parent report log"));
    }
  }

  async function markSuccess(id) {
    try {
      await parentReportingService.update(id, { status: "success" });
      await load();
    } catch (err) {
      setError(formatError(err, "Failed to update status"));
    }
  }

  async function runBiweekly() {
    setError("");
    setDispatchResult(null);
    try {
      const result = await parentReportingService.triggerBiweekly();
      setDispatchResult(result);
      await load();
    } catch (err) {
      setError(formatError(err, "Failed to trigger biweekly dispatch"));
    }
  }

  async function runHighRisk() {
    setError("");
    setDispatchResult(null);
    try {
      const result = await parentReportingService.triggerHighRisk();
      setDispatchResult(result);
      await load();
    } catch (err) {
      setError(formatError(err, "Failed to trigger high-risk dispatch"));
    }
  }

  return (
    <section className="panel">
      <h2 style={{ fontSize: 30, fontWeight: 800, color: "var(--primary)" }}>Parent Reporting</h2>
      <p className="muted">Track parent email notifications and delivery status.</p>

      {error && <p className="error-text">{typeof error === "string" ? error : JSON.stringify(error)}</p>}

      <div className="row gap-8 mb-12">
        <button className="btn primary-gradient" type="button" onClick={runBiweekly}>
          Run Biweekly Dispatch
        </button>
        <button className="btn primary-gradient" type="button" onClick={runHighRisk}>
          Run High-Risk Dispatch
        </button>
      </div>

      {dispatchResult && (
        <div className="card mb-12">
          <strong>Dispatch Result:</strong>
          <p className="muted">
            Mode: {dispatchResult.mode} | Processed: {dispatchResult.count}
          </p>
        </div>
      )}

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
          Parent Email
          <input
            required
            type="email"
            value={form.parent_email}
            onChange={(e) => setForm({ ...form, parent_email: e.target.value })}
          />
        </label>
        <label>
          Period
          <select value={form.period} onChange={(e) => setForm({ ...form, period: e.target.value })}>
            <option value="prelim">Prelim</option>
            <option value="midterm">Midterm</option>
            <option value="semi_finals">Semi-Finals</option>
            <option value="finals">Finals</option>
          </select>
        </label>
        <label>
          Attendance Summary
          <input
            value={form.attendance_summary}
            onChange={(e) => setForm({ ...form, attendance_summary: e.target.value })}
          />
        </label>
        <label>
          Risk Level
          <select value={form.risk_level} onChange={(e) => setForm({ ...form, risk_level: e.target.value })}>
            <option value="low">Low</option>
            <option value="moderate">Moderate</option>
            <option value="high">High</option>
          </select>
        </label>
        <label>
          Status
          <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
            <option value="pending">Pending</option>
            <option value="success">Success</option>
            <option value="failed">Failed</option>
          </select>
        </label>
        <label className="span-2">
          Teacher Remarks
          <input
            value={form.teacher_remarks}
            onChange={(e) => setForm({ ...form, teacher_remarks: e.target.value })}
          />
        </label>
        <button className="btn primary-gradient" type="submit">
          Create Email Log
        </button>
      </form>

      <div className="table-wrap mt-16">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Student</th>
              <th>Email</th>
              <th>Period</th>
              <th>Risk</th>
              <th>Status</th>
              <th>Sent At</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {items.map((row) => (
              <tr key={row.id}>
                <td>{row.id}</td>
                <td>{row.student_id}</td>
                <td>{row.parent_email}</td>
                <td>{row.period}</td>
                <td>{row.risk_level || "-"}</td>
                <td>{row.status}</td>
                <td>{row.sent_at || "-"}</td>
                <td>
                  {row.status !== "success" && (
                    <button className="btn" onClick={() => markSuccess(row.id)}>
                      Mark Success
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan={8} className="muted">
                  No parent email logs yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
