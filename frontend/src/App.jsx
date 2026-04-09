import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import UsersPage from "./pages/UsersPage";
import StudentsPage from "./pages/StudentsPage";
import ClassesPage from "./pages/ClassesPage";
import AttendancePage from "./pages/AttendancePage";
import GradesPage from "./pages/GradesPage";
import GradeWeightsPage from "./pages/GradeWeightsPage";
import EarlyWarningPage from "./pages/EarlyWarningPage";
import ParentReportingPage from "./pages/ParentReportingPage";
import ReportsPage from "./pages/ReportsPage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/students" element={<StudentsPage />} />
        <Route path="/classes" element={<ClassesPage />} />
        <Route path="/attendance" element={<AttendancePage />} />
        <Route path="/grades" element={<GradesPage />} />
        <Route path="/grade-weights" element={<GradeWeightsPage />} />
        <Route path="/early-warning" element={<EarlyWarningPage />} />
        <Route path="/parent-reporting" element={<ParentReportingPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route
          path="/users"
          element={
            <ProtectedRoute roles={["admin"]}>
              <UsersPage />
            </ProtectedRoute>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
