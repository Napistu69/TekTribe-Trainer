import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { BalanceDisplay } from '../economy/BalanceDisplay';
import { SettingsModal } from './SettingsModal';
import { useState } from 'react';

export function AppShell() {
  const location = useLocation();
  const navigate = useNavigate();
  const [showSettings, setShowSettings] = useState(false);

  const tabs = [
    { id: 'map', label: 'Map', icon: '🗺', path: '/' },
    { id: 'hatchery', label: 'Hatchery', icon: '🥚', path: '/hatchery' },
    { id: 'camp', label: 'Camp', icon: '🏕', path: '/camp' },
    { id: 'training', label: 'Training', icon: '⚔', path: '/training' },
    { id: 'explore', label: 'Explore', icon: '🌍', path: '/explore' },
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
            <span className="nav-icon">{tab.icon}</span>
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
