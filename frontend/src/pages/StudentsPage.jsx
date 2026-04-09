import { useEffect, useState } from "react";
import { studentsService } from "../services/crudService";

export default function StudentsPage() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({
    student_id: "",
    first_name: "",
    last_name: "",
    course: "",
    year_level: 1,
    section: ""
  });

  const load = async () => setItems(await studentsService.list());

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    await studentsService.create(form);
    setForm({ student_id: "", first_name: "", last_name: "", course: "", year_level: 1, section: "" });
    await load();
  };

  return (
    <section>
      <h2 style={{ fontSize: 30, fontWeight: 800, color: "var(--primary)" }}>Student Directory</h2>
      <p className="muted" style={{ marginTop: 4 }}>Manage student profiles and section assignments.</p>

      <form className="card form" onSubmit={submit}>
        <input placeholder="Student ID" value={form.student_id} onChange={(e)=>setForm({...form, student_id:e.target.value})} required />
        <input placeholder="First Name" value={form.first_name} onChange={(e)=>setForm({...form, first_name:e.target.value})} required />
        <input placeholder="Last Name" value={form.last_name} onChange={(e)=>setForm({...form, last_name:e.target.value})} required />
        <input placeholder="Course" value={form.course} onChange={(e)=>setForm({...form, course:e.target.value})} required />
        <input type="number" placeholder="Year Level" value={form.year_level} onChange={(e)=>setForm({...form, year_level:Number(e.target.value)})} required />
        <input placeholder="Section" value={form.section} onChange={(e)=>setForm({...form, section:e.target.value})} required />
        <button className="btn primary-gradient">Add Student</button>
      </form>

      <div className="card">
        <table className="table">
          <thead><tr><th>ID</th><th>Student ID</th><th>Name</th><th>Course</th><th>Year</th><th>Section</th></tr></thead>
          <tbody>
            {items.map((s)=>(
              <tr key={s.id}>
                <td>{s.id}</td>
                <td>{s.student_id}</td>
                <td>{s.first_name} {s.last_name}</td>
                <td>{s.course}</td>
                <td>{s.year_level}</td>
                <td>{s.section}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
