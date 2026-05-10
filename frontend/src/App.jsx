import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, useLocation, Navigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { MainLayout } from './components/layout/MainLayout';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { DevicesPage } from './pages/DevicesPage';
import { AlertsPage } from './pages/AlertsPage';
import { TechniciansPage } from './pages/TechniciansPage';
import { LocationsPage } from './pages/LocationsPage';
import { VendorsPage } from './pages/VendorsPage';
import { IncidentsPage } from './pages/IncidentsPage';
import { MaintenancePage } from './pages/MaintenancePage';
import { AuditLogPage } from './pages/AuditLogPage';
import { TopologyPage } from './pages/TopologyPage';
import { ToastContainer } from './components/ui/Toast';
import useThemeStore from './store/themeStore';
import useSocketStore from './store/socketStore';
import useAuthStore from './store/authStore';

const pageVariants = {
  initial: { opacity: 0, y: 10, scale: 0.99 },
  in: { opacity: 1, y: 0, scale: 1 },
  out: { opacity: 0, y: -10, scale: 0.99 }
};

const pageTransition = {
  type: "tween",
  ease: "anticipate",
  duration: 0.4
};

function AnimatedPage({ children }) {
  return (
    <motion.div
      initial="initial"
      animate="in"
      exit="out"
      variants={pageVariants}
      transition={pageTransition}
      className="w-full h-full"
    >
      {children}
    </motion.div>
  );
}

// Auth guard — redirects to login if not authenticated
function ProtectedRoute({ children }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function AnimatedRoutes() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/login" element={<LoginPage />} />
        
        <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
          <Route path="/" element={<AnimatedPage><DashboardPage /></AnimatedPage>} />
          <Route path="/devices" element={<AnimatedPage><DevicesPage /></AnimatedPage>} />
          <Route path="/alerts" element={<AnimatedPage><AlertsPage /></AnimatedPage>} />
          <Route path="/technicians" element={<AnimatedPage><TechniciansPage /></AnimatedPage>} />
          <Route path="/locations" element={<AnimatedPage><LocationsPage /></AnimatedPage>} />
          <Route path="/vendors" element={<AnimatedPage><VendorsPage /></AnimatedPage>} />
          <Route path="/incidents" element={<AnimatedPage><IncidentsPage /></AnimatedPage>} />
          <Route path="/maintenance" element={<AnimatedPage><MaintenancePage /></AnimatedPage>} />
          <Route path="/audit-logs" element={<AnimatedPage><AuditLogPage /></AnimatedPage>} />
          <Route path="/topology" element={<AnimatedPage><TopologyPage /></AnimatedPage>} />
        </Route>

        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  );
}

function App() {
  const initTheme = useThemeStore((s) => s.initTheme);
  const connectSocket = useSocketStore((s) => s.connect);

  useEffect(() => {
    initTheme();
    const token = localStorage.getItem('accessToken');
    if (token) {
      connectSocket();
    }
  }, [initTheme, connectSocket]);

  return (
    <BrowserRouter>
      <AnimatedRoutes />
      <ToastContainer />
    </BrowserRouter>
  );
}

export default App;
