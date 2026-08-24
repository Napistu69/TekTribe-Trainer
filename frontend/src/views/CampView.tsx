import { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';

interface Companion {
  uuid: string;
  species: string;
  name: string;
  life_stage: string;
  bond_level: number;
  care_state: {
    hunger: number;
    energy: number;
    morale: number;
    cleanliness: number;
  };
}

interface CareAction {
  action: string;
  label: string;
  icon: string;
}

const CARE_ACTIONS: CareAction[] = [
  { action: 'feed', label: 'Feed', icon: '🌿' },
  { action: 'clean', label: 'Clean', icon: '🧼' },
  { action: 'reassure', label: 'Reassure', icon: '💚' },
  { action: 'train', label: 'Train', icon: '⚡' },
];

const LIFE_STAGE_LABELS: Record<string, string> = {
  egg: '🥚 Egg',
  hatchling: '🐣 Hatchling',
  juvenile: '🦕 Juvenile',
  adult: '🦖 Adult',
  elder: '👑 Elder',
};

const COMPANION_IMAGES: Record<string, string> = {
  parasaur: '/assets/Creatures/parasaur_character.png',
  dilo: '/assets/Creatures/dilo_character.png',
  trike: '/assets/Creatures/trike_character.png',
  ptera: '/assets/Creatures/ptera_character.png',
  raptor: '/assets/Creatures/Raptor_Adult.png',
  rex: '/assets/Creatures/rex_character.png',
};

const COMPANION_SCALE: Record<string, number> = {
  parasaur: 0.7,
  dilo: 0.8,
  raptor: 0.85,
  trike: 0.9,
  ptera: 0.8,
  rex: 1.0,
};

function CareMeter({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="care-meter">
      <div className="care-meter-label">
        <span>{label}</span>
        <span>{Math.round(value * 100)}%</span>
      </div>
      <div className="meter">
        <div className="meter-fill" style={{ width: `${value * 100}%`, background: color }} />
      </div>
    </div>
  );
}

export function CampView() {
  const [companion, setCompanion] = useState<Companion | null>(null);
  const [selectedCompanion, setSelectedCompanion] = useState<string | null>(null);
  const [companions, setCompanions] = useState<Companion[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const sessionToken = useAuthStore((s) => s.sessionToken);

  const fetchCompanions = async () => {
    if (!sessionToken) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/companions`, {
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (response.ok) {
        const data = await response.json();
        setCompanions(data);
        if (data.length > 0 && !selectedCompanion) {
          setSelectedCompanion(data[0].uuid);
          setCompanion(data[0]);
        }
      }
    } catch (err) {
      console.error('Failed to fetch companions:', err);
    }
  };

  useEffect(() => {
    fetchCompanions();
  }, [sessionToken]);

  useEffect(() => {
    if (selectedCompanion) {
      const c = companions.find(c => c.uuid === selectedCompanion);
      if (c) setCompanion(c);
    }
  }, [selectedCompanion, companions]);

  const handleCareAction = async (action: string) => {
    if (!sessionToken || !selectedCompanion) return;
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/companions/${selectedCompanion}/care`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${sessionToken}` },
        body: JSON.stringify({ action }),
      });
      if (response.ok) {
        setMessage(`${action} successful!`);
        await fetchCompanions();
      } else {
        const err = await response.json();
        setMessage(err.detail || 'Care action failed');
      }
    } catch (err) {
      setMessage('Network error');
    } finally {
      setLoading(false);
    }
  };

  if (!companion) {
    return (
      <div className="camp-view">
        <h1>Camp</h1>
        <div className="empty-camp">
          <p>No companions yet. Hatch an egg to get started!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="camp-view">
      <h1>Camp</h1>

      {message && <div className="game-message">{message}</div>}

      <div className="companion-selector">
        {companions.map(c => (
          <button
            key={c.uuid}
            className={`companion-tab ${selectedCompanion === c.uuid ? 'active' : ''}`}
            onClick={() => setSelectedCompanion(c.uuid)}
          >
            {c.species}
          </button>
        ))}
      </div>

      <div className="companion-display">
        <div className="companion-visual">
          <img
            src={COMPANION_IMAGES[companion.species] || COMPANION_IMAGES.raptor}
            alt={companion.species}
            className="companion-image"
            style={{ transform: `scale(${COMPANION_SCALE[companion.species] || 1})` }}
          />
          <div className="companion-info">
            <h2>{companion.name || companion.species}</h2>
            <span className="life-stage">{LIFE_STAGE_LABELS[companion.life_stage]}</span>
            <div className="bond-bar">
              <span>Bond: {companion.bond_level}/1000</span>
              <div className="meter">
                <div className="meter-fill" style={{ width: `${(companion.bond_level / 1000) * 100}%` }} />
              </div>
            </div>
          </div>
        </div>

        <div className="care-meters">
          <CareMeter label="Hunger" value={companion.care_state.hunger} color="#ff6b6b" />
          <CareMeter label="Energy" value={companion.care_state.energy} color="#ffd93d" />
          <CareMeter label="Morale" value={companion.care_state.morale} color="#6bcb77" />
          <CareMeter label="Cleanliness" value={companion.care_state.cleanliness} color="#4d96ff" />
        </div>

        <div className="care-actions">
          {CARE_ACTIONS.map(a => (
            <button
              key={a.action}
              className="care-action-btn"
              onClick={() => handleCareAction(a.action)}
              disabled={loading}
            >
              <span className="care-icon">{a.icon}</span>
              <span className="care-label">{a.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
