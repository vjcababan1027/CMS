import { useMemo, useState } from "react";
import { reportsService } from "../services/crudService";

function toFixedSafe(value, digits = 2) {
  const n = Number(value);
  return Number.isFinite(n) ? n.toFixed(digits) : "0.00";
}

function exportCsv(filename, headers, rows) {
  const escapeCell = (v) => {
    const s = String(v ?? "");
    if (s.includes(",") || s.includes('"') || s.includes("\n")) {
      return `"${s.replace(/"/g, '""')}"`;
    }
    return s;
  };

  const csv = [
    headers.map(escapeCell).join(","),
    ...rows.map((r) => r.map(escapeCell).join(",")),
  ].join("\n");

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export default function ReportsPage() {
  const [studentId, setStudentId] = useState("");
  const [classId, setClassId] = useState("");
  const [classPerfId, setClassPerfId] = useState("");
  const [studentReport, setStudentReport] = useState(null);
  const [classPerf, setClassPerf] = useState([]);
  const [error, setError] = useState("");

  const classPerfSummary = useMemo(() => {
    if (!classPerf.length) return { avgRaw: 0, avgTransmuted: 0, highRiskCount: 0 };
    const avgRaw = classPerf.reduce((a, c) => a + Number(c.average_raw_grade || 0), 0) / classPerf.length;
    const avgTransmuted =
      classPerf.reduce((a, c) => a + Number(c.average_transmuted_grade || 0), 0) / classPerf.length;
    const highRiskCount = classPerf.filter((x) => String(x.latest_risk_level || "").toLowerCase() === "high").length;
    return { avgRaw, avgTransmuted, highRiskCount };
  }, [classPerf]);

  async function loadStudentReport(e) {
    e.preventDefault();
    setError("");
    try {
      const data = await reportsService.studentClass(studentId, classId);
      setStudentReport(data);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to load student class report");
    }
  }

  async function loadClassPerformance(e) {
    e.preventDefault();
    setError("");
    try {
      const data = await reportsService.classPerformance(classPerfId);
      setClassPerf(data);
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to load class performance report");
    }
  }

  function handleExportStudentCsv() {
    if (!studentReport) return;
    const rows = [];
    for (const p of studentReport.period_summaries || []) {
      rows.push([
        "period-summary",
        p.period,
        toFixedSafe(p.raw_grade),
        toFixedSafe(p.transmuted_grade),
        "",
        "",
        "",
        "",
      ]);
      const cb = p.component_breakdown || {};
      for (const [component, values] of Object.entries(cb)) {
        rows.push([
          "component-breakdown",
          p.period,
          "",
          "",
          component,
          toFixedSafe(values?.weight_percent),
          toFixedSafe(values?.weighted_score),
          toFixedSafe(values?.raw_score),
        ]);
      }
    }

    exportCsv(
      `student_report_s${studentReport.student_id}_c${studentReport.class_id}.csv`,
      [
        "row_type",
        "period",
        "raw_grade",
        "transmuted_grade",
        "component",
        "weight_percent",
        "weighted_score",
        "raw_score",
      ],
      [
        ["meta", "", "", "", "student_id", studentReport.student_id, "class_id", studentReport.class_id],
        ["meta", "", toFixedSafe(studentReport.overall_raw_grade), toFixedSafe(studentReport.overall_transmuted_grade), "overall", "", "", ""],
        ...rows,
      ]
    );
  }

  function handleExportClassPerfCsv() {
    if (!classPerf.length) return;
    const rows = classPerf.map((r) => [
      r.student_id,
      r.student_code || "",
      r.student_name || "",
      toFixedSafe(r.average_raw_grade),
      toFixedSafe(r.average_transmuted_grade),
      r.latest_risk_level || "",
    ]);
    exportCsv(
      `class_performance_c${classPerfId || "unknown"}.csv`,
      ["student_id", "student_code", "student_name", "average_raw_grade", "average_transmuted_grade", "latest_risk_level"],
      rows
    );
  }

  return (
    <section className="panel reports-page">
      <h2 style={{ fontSize: 30, fontWeight: 800, color: "var(--primary)" }}>Reports & Analytics</h2>
      <p className="muted">Grade summaries, component breakdown, class performance charts, and exports.</p>
      {error && <p className="error-text">{String(error)}</p>}

      <form className="form-grid" onSubmit={loadStudentReport}>
        <label>
          Student ID
          <input value={studentId} onChange={(e) => setStudentId(e.target.value)} required />
        </label>
        <label>
          Class ID
          <input value={classId} onChange={(e) => setClassId(e.target.value)} required />
        </label>
        <button className="btn primary-gradient" type="submit">Load Student Report</button>
      </form>

      {studentReport && (
        <div className="table-wrap mt-16 report-section">
          <div className="report-actions">
            <h3>Student/Class Summary</h3>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <button className="btn secondary" type="button" onClick={handleExportStudentCsv}>Export Student CSV</button>
              <button className="btn" type="button" onClick={() => window.print()}>Export PDF (Print)</button>
            </div>
          </div>

          <div className="reports-cards">
            <div className="report-card"><h4>Overall Raw</h4><p>{toFixedSafe(studentReport.overall_raw_grade)}</p></div>
            <div className="report-card"><h4>Overall Transmuted</h4><p>{toFixedSafe(studentReport.overall_transmuted_grade)}</p></div>
            <div className="report-card"><h4>Periods</h4><p>{(studentReport.period_summaries || []).length}</p></div>
          </div>

          <table>
            <thead>
              <tr>
                <th>Period</th>
                <th>Raw</th>
                <th>Transmuted</th>
              </tr>
            </thead>
            <tbody>
              {(studentReport.period_summaries || []).map((p) => (
                <tr key={p.period}>
                  <td>{p.period}</td>
                  <td>{toFixedSafe(p.raw_grade)}</td>
                  <td>{toFixedSafe(p.transmuted_grade)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {(studentReport.period_summaries || []).map((p) => (
            <div key={`${p.period}-breakdown`} className="component-breakdown">
              <h4>{p.period} Component Breakdown</h4>
              <table>
                <thead>
                  <tr>
                    <th>Component</th>
                    <th>Weight %</th>
                    <th>Weighted Score</th>
                    <th>Raw Score</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(p.component_breakdown || {}).map(([component, values]) => (
                    <tr key={`${p.period}-${component}`}>
                      <td>{component}</td>
                      <td>{toFixedSafe(values?.weight_percent)}</td>
                      <td>{toFixedSafe(values?.weighted_score)}</td>
                      <td>{toFixedSafe(values?.raw_score)}</td>
                    </tr>
                  ))}
                  {!Object.keys(p.component_breakdown || {}).length && (
                    <tr>
                      <td colSpan={4} className="muted">No component data for this period.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      )}

      <form className="form-grid mt-16" onSubmit={loadClassPerformance}>
        <label>
          Class ID
          <input value={classPerfId} onChange={(e) => setClassPerfId(e.target.value)} required />
        </label>
        <button className="btn primary-gradient" type="submit">Load Class Performance</button>
      </form>

      <div className="table-wrap mt-16 report-section">
        <div className="report-actions">
          <h3>Class Performance</h3>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button className="btn secondary" type="button" onClick={handleExportClassPerfCsv}>Export Class CSV</button>
            <button className="btn" type="button" onClick={() => window.print()}>Export PDF (Print)</button>
          </div>
        </div>

        <div className="reports-cards">
          <div className="report-card"><h4>Students</h4><p>{classPerf.length}</p></div>
          <div className="report-card"><h4>Class Avg Raw</h4><p>{toFixedSafe(classPerfSummary.avgRaw)}</p></div>
          <div className="report-card"><h4>Class Avg Transmuted</h4><p>{toFixedSafe(classPerfSummary.avgTransmuted)}</p></div>
          <div className="report-card"><h4>High Risk</h4><p>{classPerfSummary.highRiskCount}</p></div>
        </div>

        <div className="perf-bars">
          {classPerf.map((r) => {
            const width = Math.max(0, Math.min(100, Number(r.average_raw_grade || 0)));
            return (
              <div key={`bar-${r.student_id}`} className="perf-bar-row">
                <div className="perf-bar-label">{r.student_name || r.student_code || `Student ${r.student_id}`}</div>
                <div className="perf-bar-track">
                  <div className="perf-bar-fill" style={{ width: `${width}%` }} />
                </div>
                <div className="perf-bar-value">{toFixedSafe(r.average_raw_grade)}</div>
              </div>
            );
          })}
          {classPerf.length === 0 && <p className="muted">No performance records.</p>}
        </div>

        <table>
          <thead>
            <tr>
              <th>Student</th>
              <th>Avg Raw</th>
              <th>Avg Transmuted</th>
              <th>Latest Risk</th>
            </tr>
          </thead>
          <tbody>
            {classPerf.map((r) => (
              <tr key={r.student_id}>
                <td>{r.student_name || r.student_code || r.student_id}</td>
                <td>{toFixedSafe(r.average_raw_grade)}</td>
                <td>{toFixedSafe(r.average_transmuted_grade)}</td>
                <td>{r.latest_risk_level || "-"}</td>
              </tr>
            ))}
            {classPerf.length === 0 && (
              <tr>
                <td colSpan={4} className="muted">No performance records.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
