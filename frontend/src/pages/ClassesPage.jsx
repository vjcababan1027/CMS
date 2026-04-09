import { useEffect, useState } from "react";
import { classesService } from "../services/crudService";

export default function ClassesPage() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({
    class_code: "",
    name: "",
    subject: "",
    teacher_id: 2,
    academic_year: "2025-2026",
    term: "1st"
  });

  const load = async () => setItems(await classesService.list());

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    await classesService.create(form);
    setForm({ class_code: "", name: "", subject: "", teacher_id: 2, academic_year: "2025-2026", term: "1st" });
    await load();
  };

  return (
    <section>
      <h2 style={{ fontSize: 30, fontWeight: 800, color: "var(--primary)" }}>Class Management</h2>
      <p className="muted" style={{ marginTop: 4 }}>Create and manage class sections by code.</p>

      <form className="card form" onSubmit={submit}>
        <input placeholder="Class Code" value={form.class_code} onChange={(e)=>setForm({...form, class_code:e.target.value})} required />
        <input placeholder="Name" value={form.name} onChange={(e)=>setForm({...form, name:e.target.value})} required />
        <input placeholder="Subject" value={form.subject} onChange={(e)=>setForm({...form, subject:e.target.value})} required />
        <input type="number" placeholder="Teacher ID" value={form.teacher_id} onChange={(e)=>setForm({...form, teacher_id:Number(e.target.value)})} required />
        <input placeholder="Academic Year" value={form.academic_year} onChange={(e)=>setForm({...form, academic_year:e.target.value})} required />
        <input placeholder="Term" value={form.term} onChange={(e)=>setForm({...form, term:e.target.value})} required />
        <button className="btn primary-gradient">Create New Class</button>
      </form>

      <div className="card">
        <table className="table">
          <thead><tr><th>ID</th><th>Code</th><th>Name</th><th>Subject</th><th>Teacher</th><th>Year</th><th>Term</th></tr></thead>
          <tbody>
            {items.map((c)=>(
              <tr key={c.id}>
                <td>{c.id}</td><td>{c.class_code}</td><td>{c.name}</td><td>{c.subject}</td><td>{c.teacher_id}</td><td>{c.academic_year}</td><td>{c.term}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
