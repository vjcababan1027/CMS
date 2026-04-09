import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const navItems = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/classes", label: "Classes" },
  { to: "/students", label: "Students" },
  { to: "/attendance", label: "Attendance" },
  { to: "/grades", label: "Grade Monitoring" },
  { to: "/grade-weights", label: "Grade Weights" },
  { to: "/early-warning", label: "Alerts" },
  { to: "/parent-reporting", label: "Parent Reporting" },
  { to: "/reports", label: "Reports" },
  { to: "/users", label: "User Management", adminOnly: true }
];

export default function Layout() {
  const { user, logout } = useAuth();
  const isAdmin = user?.role === "admin";

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1>Academic Architect</h1>
        <p className="sidebar-subtitle">{isAdmin ? "Administrative Portal" : "Faculty Portal"}</p>
        <nav>
          {navItems
            .filter((item) => !item.adminOnly || isAdmin)
            .map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
              >
                {item.label}
              </NavLink>
            ))}
        </nav>
        <button className="btn danger mt-auto" onClick={logout}>
          Logout
        </button>
      </aside>
      <main className="content">
        <header className="topbar">
          <div>
            <strong>{user?.full_name || "User"}</strong>
            <p className="muted" style={{ textTransform: "capitalize" }}>{user?.role || "faculty"}</p>
          </div>
          <div className="muted">Institutional Grade Monitoring</div>
        </header>
        <div className="page">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
