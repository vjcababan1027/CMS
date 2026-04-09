import { useEffect, useState } from "react";
import { classesService, studentsService, gradesService, attendanceService } from "../services/crudService";

export default function DashboardPage() {
  const [stats, setStats] = useState({
    students: 0,
    classes: 0,
    grades: 0,
    attendance: 0
  });

  useEffect(() => {
    (async () => {
      try {
        const [students, classes, grades, attendance] = await Promise.all([
          studentsService.list(),
          classesService.list(),
          gradesService.list(),
          attendanceService.list()
        ]);
        setStats({
          students: students.length,
          classes: classes.length,
          grades: grades.length,
          attendance: attendance.length
        });
      } catch {
        // no-op
      }
    })();
  }, []);

  return (
    <section>
      <h2 style={{ fontSize: 32, fontWeight: 800, color: "var(--primary)" }}>Institutional Grade Monitoring</h2>
      <p className="muted" style={{ marginTop: 6 }}>Live summary based on current system records.</p>

      <div className="grid cards" style={{ marginTop: 18 }}>
        <div className="card">
          <p className="muted" style={{ textTransform: "uppercase", fontWeight: 700, fontSize: 11 }}>Total Students</p>
          <h3 style={{ fontSize: 34, marginTop: 8 }}>{stats.students}</h3>
        </div>
        <div className="card">
          <p className="muted" style={{ textTransform: "uppercase", fontWeight: 700, fontSize: 11 }}>Total Classes</p>
          <h3 style={{ fontSize: 34, marginTop: 8 }}>{stats.classes}</h3>
        </div>
        <div className="card">
          <p className="muted" style={{ textTransform: "uppercase", fontWeight: 700, fontSize: 11 }}>Grade Records</p>
          <h3 style={{ fontSize: 34, marginTop: 8 }}>{stats.grades}</h3>
        </div>
        <div className="card">
          <p className="muted" style={{ textTransform: "uppercase", fontWeight: 700, fontSize: 11 }}>Attendance Logs</p>
          <h3 style={{ fontSize: 34, marginTop: 8 }}>{stats.attendance}</h3>
        </div>
      </div>

      <div className="card" style={{ marginTop: 18 }}>
        <h3 style={{ fontSize: 18, fontWeight: 800, marginBottom: 12 }}>Departmental Distribution (Preview)</h3>
        <div style={{ display: "grid", gap: 12 }}>
          {[
            { dept: "Computer Science & IT", pct: 85 },
            { dept: "Mechanical Engineering", pct: 70 },
            { dept: "English Literature", pct: 92 },
            { dept: "Biological Sciences", pct: 65 }
          ].map((row) => (
            <div key={row.dept}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, fontWeight: 700 }}>
                <span>{row.dept}</span>
                <span style={{ color: "var(--primary)" }}>{row.pct}%</span>
              </div>
              <div style={{ height: 8, width: "100%", background: "#e2e8f0", borderRadius: 99, overflow: "hidden", marginTop: 6 }}>
                <div className="primary-gradient" style={{ height: "100%", width: `${row.pct}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
