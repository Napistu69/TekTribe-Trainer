import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { SettingsModal } from './SettingsModal';
import { WalletModal } from './WalletModal';
import { useState } from 'react';
import { useEconomyStore } from '../../stores/economyStore';

export function AppShell() {
  const location = useLocation();
  const navigate = useNavigate();
  const [showSettings, setShowSettings] = useState(false);
  const [showWallet, setShowWallet] = useState(false);
  const dust = useEconomyStore((s) => s.dust);

  const tabs = [
    { id: 'map', label: 'Map', image: '/assets/Habitat & Camp/habitat.png', path: '/' },
    { id: 'hatchery', label: 'Hatchery', image: '/assets/Habitat & Camp/hatchery.png', path: '/hatchery' },
    { id: 'nursery', label: 'Nursery', image: '/assets/Habitat & Camp/nursery.png', path: '/nursery' },
    { id: 'camp', label: 'Camp', image: '/assets/Habitat & Camp/camp_bg.jpg', path: '/camp' },
    { id: 'training', label: 'Training', image: '/assets/Habitat & Camp/training_grounds.png', path: '/training' },
    { id: 'explore', label: 'Explore', image: '/assets/Habitat & Camp/expedition_gate.png', path: '/explore' },
    { id: 'shop', label: 'Shop', image: '/assets/Currency & Resource/ELE_Dust.png', path: '/economy' },
  ];

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="header-left">
          <div className="overseer-avatar-small" />
          <span className="app-title">TekTribe Trainer</span>
        </div>
        <div className="header-right">
          <button className="wallet-btn" onClick={() => setShowWallet(true)} aria-label="Open Wallet">
            ✦ <span className="wallet-balance-display">{dust.toLocaleString()}</span>
          </button>
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
            <img src={tab.image} alt="" className="nav-image" />
            <span className="nav-label">{tab.label}</span>
          </button>
        ))}
      </nav>

      {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
      {showWallet && <WalletModal onClose={() => setShowWallet(false)} />}
    </div>
  );
}
