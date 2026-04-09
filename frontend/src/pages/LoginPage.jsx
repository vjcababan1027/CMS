import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const ROLE_CREDENTIALS = {
  admin: { email: "admin@cms.local", password: "admin1234!" },
  teacher: { email: "teacher@cms.local", password: "teacher1234!" }
};

export default function LoginPage() {
  const { login, isAuthenticated, loading } = useAuth();
  const [selectedRole, setSelectedRole] = useState("admin");
  const [email, setEmail] = useState(ROLE_CREDENTIALS.admin.email);
  const [password, setPassword] = useState(ROLE_CREDENTIALS.admin.password);
  const [error, setError] = useState("");

  if (isAuthenticated) return <Navigate to="/dashboard" replace />;

  const applyRole = (role) => {
    setSelectedRole(role);
    setEmail(ROLE_CREDENTIALS[role].email);
    setPassword(ROLE_CREDENTIALS[role].password);
    setError("");
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    const res = await login(email, password);
    if (!res.ok) setError(res.message);
  };

  return (
    <div style={{ minHeight: "100vh", display: "grid", gridTemplateColumns: "1.2fr 1fr" }}>
      <section className="primary-gradient" style={{ color: "white", padding: 48, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
        <div>
          <h1 style={{ fontSize: 34, fontWeight: 800 }}>Academic Architect</h1>
          <p style={{ opacity: 0.8, letterSpacing: "0.12em", textTransform: "uppercase", fontSize: 11, marginTop: 6 }}>
            Decision Support Platform
          </p>
        </div>
        <div>
          <h2 style={{ fontSize: 42, lineHeight: 1.2, marginBottom: 14 }}>Precision for Institutional Excellence.</h2>
          <p style={{ opacity: 0.9 }}>Empowering administrators and educators with curated analytics and interventions.</p>
        </div>
        <div style={{ opacity: 0.7, fontSize: 12 }}>© 2024 Academic Architect System</div>
      </section>
      <section style={{ background: "#fff", display: "grid", placeItems: "center", padding: 24 }}>
        <form className="card form" onSubmit={onSubmit} style={{ width: "100%", maxWidth: 460, marginTop: 0 }}>
          <h2 style={{ fontSize: 30, fontWeight: 800 }}>System Portal</h2>
          <p className="muted">Choose role and authenticate using institutional credentials.</p>

          <label>Login As</label>
          <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
            <button
              type="button"
              className="btn"
              onClick={() => applyRole("admin")}
              style={{
                flex: 1,
                border: selectedRole === "admin" ? "2px solid #111827" : "1px solid #d1d5db",
                background: selectedRole === "admin" ? "#eef2ff" : "#fff",
                color: "#111827"
              }}
            >
              Admin
            </button>
            <button
              type="button"
              className="btn"
              onClick={() => applyRole("teacher")}
              style={{
                flex: 1,
                border: selectedRole === "teacher" ? "2px solid #111827" : "1px solid #d1d5db",
                background: selectedRole === "teacher" ? "#eef2ff" : "#fff",
                color: "#111827"
              }}
            >
              Teacher
            </button>
          </div>

          <label>Institutional Email</label>
          <input value={email} onChange={(e) => setEmail(e.target.value)} required />
          <label>Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          {error && <div className="error">{error}</div>}
          <button className="btn primary-gradient" disabled={loading}>
            {loading ? "Signing in..." : `Sign In as ${selectedRole === "admin" ? "Admin" : "Teacher"}`}
          </button>
        </form>
      </section>
    </div>
  );
}
