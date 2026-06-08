import { Suspense, lazy } from "react";
import { Routes, Route } from "react-router-dom";

const DispatcherDashboard = lazy(() => import("@/pages/DispatcherDashboard"));
const AdminPanel = lazy(() => import("@/pages/AdminPanel"));
const DriverView = lazy(() => import("@/pages/DriverView"));
const LiveTracking = lazy(() => import("@/pages/LiveTracking"));
const LoginPage = lazy(() => import("@/pages/LoginPage"));

export default function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Routes>
        <Route path="/" element={<DispatcherDashboard />} />
        <Route path="/admin" element={<AdminPanel />} />
        <Route path="/driver" element={<DriverView />} />
        <Route path="/tracking" element={<LiveTracking />} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </Suspense>
  );
}
