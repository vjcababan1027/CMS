import { useEffect, useState } from "react";
import { gradesService } from "../services/crudService";

export default function GradesPage() {
  const [items, setItems] = useState([]);
  const [calc, setCalc] = useState(null);
  const [form, setForm] = useState({
    student_id: "",
    class_id: "",
    period: "prelim",
    component: "quizzes",
    score: 0
  });

  const load = async () => setItems(await gradesService.list());

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    await gradesService.create({
      ...form,
      student_id: Number(form.student_id),
      class_id: Number(form.class_id),
      score: Number(form.score)
    });
    await load();
  };

  const calculate = async () => {
    const data = await gradesService.calculatePath({
      student_id: Number(form.student_id),
      class_id: Number(form.class_id),
      period: form.period
    });
    setCalc(data);
  };

  return (
    <section>
      <h2 style={{ fontSize: 30, fontWeight: 800, color: "var(--primary)" }}>Grade Monitoring</h2>
      <p className="muted" style={{ marginTop: 4 }}>Encode component grades and compute final results.</p>

      <form className="card form" onSubmit={submit}>
        <input placeholder="Student ID" value={form.student_id} onChange={(e)=>setForm({...form, student_id:e.target.value})} required />
        <input placeholder="Class ID" value={form.class_id} onChange={(e)=>setForm({...form, class_id:e.target.value})} required />
        <select value={form.period} onChange={(e)=>setForm({...form, period:e.target.value})}>
          <option value="prelim">prelim</option>
          <option value="midterm">midterm</option>
          <option value="semi_finals">semi_finals</option>
          <option value="finals">finals</option>
        </select>
        <select value={form.component} onChange={(e)=>setForm({...form, component:e.target.value})}>
          <option value="quizzes">quizzes</option>
          <option value="oral_participation">oral_participation</option>
          <option value="graded_activity">graded_activity</option>
          <option value="attendance">attendance</option>
          <option value="major_exam">major_exam</option>
        </select>
        <input type="number" step="0.01" placeholder="Score" value={form.score} onChange={(e)=>setForm({...form, score:e.target.value})} required />
        <button className="btn primary-gradient">Add Grade</button>
        <button className="btn secondary" type="button" onClick={calculate}>Calculate Final</button>
      </form>

      {calc && (
        <div className="card">
          <h3 style={{ marginBottom: 8 }}>Calculation Result</h3>
          <p>Raw Grade: {calc.raw_grade}</p>
          <p>Transmuted Grade: {calc.transmuted_grade}</p>
        </div>
      )}

      <div className="card">
        <table className="table">
          <thead><tr><th>ID</th><th>Student</th><th>Class</th><th>Period</th><th>Component</th><th>Score</th><th>Weight</th></tr></thead>
          <tbody>
            {items.map((g)=>(
              <tr key={g.id}>
                <td>{g.id}</td><td>{g.student_id}</td><td>{g.class_id}</td><td>{g.period}</td><td>{g.component}</td><td>{g.score}</td><td>{g.weight_percentage}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
