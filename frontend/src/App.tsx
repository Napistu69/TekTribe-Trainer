import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { initPassport } from './lib/passport';
import { registerServiceWorker } from './service-worker-registration';
import { OverseerDialog } from './components/overseer/OverseerDialog';
import { HatcheryView } from './views/HatcheryView';
import { CampView } from './views/CampView';
import { TrainingSelect } from './components/training/TrainingSelect';
import { ExpeditionMap } from './components/expedition/ExpeditionMap';
import { LoginScreen } from './components/auth/LoginScreen';
import { AuthGuard } from './components/auth/AuthGuard';
import { CallbackPage } from './components/auth/CallbackPage';
import { useEffect } from 'react';
import './index.css';

function App() {
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
        <Route path="/login" element={<LoginScreen />} />
        <Route path="/callback" element={<CallbackPage />} />
        <Route
          path="/"
          element={
            <AuthGuard>
              <AppShell />
            </AuthGuard>
          }
        >
          <Route index element={<HatcheryView />} />
          <Route path="camp" element={<CampView />} />
          <Route path="training" element={<TrainingSelect companionSpecies="" onSelect={() => {}} />} />
          <Route path="explore" element={<ExpeditionMap onSelectBiome={() => {}} />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <OverseerDialog />
    </BrowserRouter>
  );
}

export default App;
