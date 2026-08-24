import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { BalanceDisplay } from '../economy/BalanceDisplay';
import { SettingsModal } from './SettingsModal';
import { useState } from 'react';

export function AppShell() {
  const location = useLocation();
  const navigate = useNavigate();
  const [showSettings, setShowSettings] = useState(false);

  const tabs = [
    { id: 'map', label: 'Map', image: '/assets/Habitat & Camp/habitat.png', path: '/' },
    { id: 'hatchery', label: 'Hatchery', image: '/assets/Habitat & Camp/hatchery.png', path: '/hatchery' },
    { id: 'camp', label: 'Camp', image: '/assets/Habitat & Camp/nursery.png', path: '/camp' },
    { id: 'training', label: 'Training', image: '/assets/Habitat & Camp/habitat.png', path: '/training' },
    { id: 'explore', label: 'Explore', image: '/assets/Habitat & Camp/expedition_gate.png', path: '/explore' },
    { id: 'overseer', label: 'Overseer', image: '/assets/Overseer & Lore/overseer.png', path: '/overseer' },
  ];

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="header-left">
          <div className="overseer-avatar-small" />
          <span className="app-title">TekTribe</span>
        </div>
        <div className="header-right">
          <BalanceDisplay compact />
          <button
            className="icon-btn"
            onClick={() => setShowSettings(true)}
            aria-label="Settings"
          >
            ⚙
          </button>
        </div>
      </header>

      <main className="app-content">
        <Outlet />
      </main>

      <nav className="bottom-nav">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`nav-tab ${location.pathname === tab.path ? 'active' : ''}`}
            onClick={() => navigate(tab.path)}
          >
            <img src={tab.image} alt={tab.label} className="nav-image" />
            <span className="nav-label">{tab.label}</span>
          </button>
        ))}
      </nav>

      {showSettings && (
        <SettingsModal onClose={() => setShowSettings(false)} />
      )}
    </div>
  );
}
