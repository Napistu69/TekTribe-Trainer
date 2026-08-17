import { useEffect } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { initPassport } from './lib/passport';
import { registerServiceWorker } from './service-worker-registration';
import { AuthGuard } from './components/auth/AuthGuard';
import { LoginScreen } from './components/auth/LoginScreen';
import { useAuthStore } from './stores/authStore';
import './index.css';

function App() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  // Initialize service worker
  useEffect(() => {
    registerServiceWorker();
  }, []);

  // Initialize Passport SDK
  useEffect(() => {
    const clientId = import.meta.env.VITE_CLIENT_ID;
    const redirectUri = `${window.location.origin}/callback`;
    
    if (clientId) {
      initPassport(clientId, redirectUri);
    }
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route
          path="/login"
          element={
            isAuthenticated ? <Navigate to="/" replace /> : <LoginScreen />
          }
        />

        {/* Protected routes */}
        <Route
          path="/"
          element={
            <AuthGuard>
              <div className="app-shell">
                <div className="loading-screen">
                  <h1>TekTribe Trainer</h1>
                  <p>Loading the Hatchery...</p>
                </div>
              </div>
            </AuthGuard>
          }
        />

        {/* Catch all - redirect to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
