import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { initPassport } from './lib/passport';
import { registerServiceWorker } from './service-worker-registration';
import { OverseerDialog } from './components/overseer/OverseerDialog';
import { useAuthStore } from './stores/authStore';
import { HatcheryView } from './views/HatcheryView';
import { CampView } from './views/CampView';
import { TrainingSelect } from './components/training/TrainingSelect';
import { ExpeditionMap } from './components/expedition/ExpeditionMap';
import { useEffect } from 'react';
import './index.css';

function App() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  useEffect(() => {
    registerServiceWorker();
  }, []);

  useEffect(() => {
    const clientId = import.meta.env.VITE_CLIENT_ID;
    if (clientId) {
      initPassport(clientId, `${window.location.origin}/callback`);
    }
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={
            isAuthenticated ? <Navigate to="/" replace /> : <div>Login</div>
          }
        />
        {isAuthenticated && (
          <Route element={<AppShell />}>
            <Route path="/" element={<HatcheryView />} />
            <Route path="/camp" element={<CampView />} />
            <Route path="/training" element={<TrainingSelect companionSpecies="" onSelect={() => {}} />} />
            <Route path="/explore" element={<ExpeditionMap onSelectBiome={() => {}} />} />
          </Route>
        )}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <OverseerDialog />
    </BrowserRouter>
  );
}

export default App;
