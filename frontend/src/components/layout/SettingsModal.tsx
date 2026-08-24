import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';
import { logoutPassport } from '../../lib/passport';

interface SettingsModalProps {
  onClose: () => void;
}

export function SettingsModal({ onClose }: SettingsModalProps) {
  const navigate = useNavigate();
  const logout = useAuthStore((s) => s.logout);

  const handleLogout = async () => {
    try {
      await logoutPassport();
    } catch (e) {
      // Ignore errors
    }
    logout();
    onClose();
    navigate('/login');
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <button className="modal-close" onClick={onClose}>
          ✕
        </button>
        <h2>Settings</h2>

        <div className="settings-section">
          <div className="setting-row">
            <span>Sound</span>
            <label className="toggle">
              <input type="checkbox" defaultChecked />
              <span className="toggle-slider" />
            </label>
          </div>
          <div className="setting-row">
            <span>Notifications</span>
            <label className="toggle">
              <input type="checkbox" defaultChecked />
              <span className="toggle-slider" />
            </label>
          </div>
        </div>

        <div className="settings-section">
          <label>Language</label>
          <select disabled>
            <option>English</option>
            <option>Coming soon</option>
          </select>
        </div>

        <div className="settings-section">
          <button className="btn-secondary" onClick={handleLogout}>
            Log Out
          </button>
        </div>
      </div>
    </div>
  );
}
