import { useEffect, useState } from "react";
import { gradeWeightsService } from "../services/crudService";

export default function GradeWeightsPage() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({
    class_id: "",
    period: "prelim",
    quizzes_weight: 0.2,
    oral_participation_weight: 0.1,
    graded_activity_weight: 0.2,
    attendance_weight: 0.1,
    major_exam_weight: 0.4
  });

  const load = async () => setItems(await gradeWeightsService.list());

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    await gradeWeightsService.create({
      ...form,
      class_id: Number(form.class_id),
      quizzes_weight: Number(form.quizzes_weight),
      oral_participation_weight: Number(form.oral_participation_weight),
      graded_activity_weight: Number(form.graded_activity_weight),
      attendance_weight: Number(form.attendance_weight),
      major_exam_weight: Number(form.major_exam_weight)
    });
    await load();
  };

  return (
    <section>
      <h2 style={{ fontSize: 30, fontWeight: 800, color: "var(--primary)" }}>Grading Weights</h2>
      <p className="muted" style={{ marginTop: 4 }}>Configure component percentages per grading period.</p>
      <form className="card form" onSubmit={submit}>
        <input placeholder="Class ID" value={form.class_id} onChange={(e)=>setForm({...form, class_id:e.target.value})} required />
        <select value={form.period} onChange={(e)=>setForm({...form, period:e.target.value})}>
          <option value="prelim">prelim</option>
          <option value="midterm">midterm</option>
          <option value="semi_finals">semi_finals</option>
          <option value="finals">finals</option>
        </select>
        <input type="number" step="0.01" value={form.quizzes_weight} onChange={(e)=>setForm({...form, quizzes_weight:e.target.value})} />
        <input type="number" step="0.01" value={form.oral_participation_weight} onChange={(e)=>setForm({...form, oral_participation_weight:e.target.value})} />
        <input type="number" step="0.01" value={form.graded_activity_weight} onChange={(e)=>setForm({...form, graded_activity_weight:e.target.value})} />
        <input type="number" step="0.01" value={form.attendance_weight} onChange={(e)=>setForm({...form, attendance_weight:e.target.value})} />
        <input type="number" step="0.01" value={form.major_exam_weight} onChange={(e)=>setForm({...form, major_exam_weight:e.target.value})} />
        <button className="btn primary-gradient">Save Weights</button>
      </form>

      <div className="card">
        <table className="table">
          <thead><tr><th>ID</th><th>Class</th><th>Period</th><th>Q</th><th>O</th><th>GA</th><th>A</th><th>ME</th></tr></thead>
          <tbody>
            {items.map((w)=>(
              <tr key={w.id}>
                <td>{w.id}</td><td>{w.class_id}</td><td>{w.period}</td>
                <td>{w.quizzes_weight}</td><td>{w.oral_participation_weight}</td><td>{w.graded_activity_weight}</td><td>{w.attendance_weight}</td><td>{w.major_exam_weight}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
