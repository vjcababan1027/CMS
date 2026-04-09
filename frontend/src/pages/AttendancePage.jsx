import { useEffect, useState } from "react";
import { attendanceService } from "../services/crudService";

export default function AttendancePage() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({
    student_id: "",
    class_id: "",
    date: "",
    status: "present",
    recorded_by: 2
  });

  const load = async () => setItems(await attendanceService.list());

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    await attendanceService.create({
      ...form,
      student_id: Number(form.student_id),
      class_id: Number(form.class_id),
      recorded_by: Number(form.recorded_by)
    });
    setForm({ student_id: "", class_id: "", date: "", status: "present", recorded_by: 2 });
    await load();
  };

  return (
    <section>
      <h2 style={{ fontSize: 30, fontWeight: 800, color: "var(--primary)" }}>Real-time Attendance</h2>
      <p className="muted" style={{ marginTop: 4 }}>Record and monitor attendance status per session.</p>

      <form className="card form" onSubmit={submit}>
        <input placeholder="Student ID" value={form.student_id} onChange={(e)=>setForm({...form, student_id:e.target.value})} required />
        <input placeholder="Class ID" value={form.class_id} onChange={(e)=>setForm({...form, class_id:e.target.value})} required />
        <input type="datetime-local" value={form.date} onChange={(e)=>setForm({...form, date:e.target.value})} required />
        <select value={form.status} onChange={(e)=>setForm({...form, status:e.target.value})}>
          <option value="present">present</option>
          <option value="absent">absent</option>
          <option value="tardy">tardy</option>
          <option value="excused">excused</option>
        </select>
        <input placeholder="Recorded By (User ID)" value={form.recorded_by} onChange={(e)=>setForm({...form, recorded_by:e.target.value})} required />
        <button className="btn primary-gradient">Record Attendance</button>
      </form>

      <div className="card">
        <table className="table">
          <thead><tr><th>ID</th><th>Student</th><th>Class</th><th>Date</th><th>Status</th><th>Recorder</th></tr></thead>
          <tbody>
            {items.map((a)=>(
              <tr key={a.id}>
                <td>{a.id}</td><td>{a.student_id}</td><td>{a.class_id}</td><td>{a.date}</td><td>{a.status}</td><td>{a.recorded_by}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
