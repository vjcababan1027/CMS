import { useEffect, useState } from "react";
import { usersService } from "../services/crudService";

export default function UsersPage() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({
    email: "",
    password: "",
    full_name: "",
    role: "teacher"
  });

  const load = async () => setItems(await usersService.list());

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    await usersService.create(form);
    setForm({ email: "", password: "", full_name: "", role: "teacher" });
    await load();
  };

  return (
    <section>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "end", marginBottom: 14 }}>
        <div>
          <h2 style={{ fontSize: 30, fontWeight: 800, color: "var(--primary)" }}>Staff & Faculty Directory</h2>
          <p className="muted">Manage institutional access and roles.</p>
        </div>
      </div>

      <form className="card form" onSubmit={submit}>
        <input placeholder="Full name" value={form.full_name} onChange={(e)=>setForm({...form, full_name:e.target.value})} required />
        <input placeholder="Email" value={form.email} onChange={(e)=>setForm({...form, email:e.target.value})} required />
        <input type="password" placeholder="Password" value={form.password} onChange={(e)=>setForm({...form, password:e.target.value})} required />
        <select value={form.role} onChange={(e)=>setForm({...form, role:e.target.value})}>
          <option value="teacher">Teacher</option>
          <option value="admin">Admin</option>
        </select>
        <button className="btn primary-gradient">Add New User</button>
      </form>

      <div className="card">
        <table className="table">
          <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Role</th></tr></thead>
          <tbody>
            {items.map((u)=>(
              <tr key={u.id}><td>{u.id}</td><td>{u.full_name}</td><td>{u.email}</td><td>{u.role}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
