import { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { PhaserGame } from '../components/game/PhaserGame';

interface Egg {
  uuid: string;
  rarity: string;
  source: string;
  pulled_at: string;
  incubation_started_at: string | null;
  temperature: number;
  stability: number;
}

const RARITY_COLORS: Record<string, string> = {
  common: '#808080',
  uncommon: '#00ff00',
  rare: '#0080ff',
  epic: '#ff00ff',
  ascendant: '#00ffff',
  legendary: '#ffd700',
  mythic: '#ff0000',
};

export function HatcheryView() {
  const [eggs, setEggs] = useState<Egg[]>([]);
  const [selectedEgg, setSelectedEgg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const sessionToken = useAuthStore((s) => s.sessionToken);

  const fetchEggs = async () => {
    if (!sessionToken) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/eggs`, {
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (response.ok) {
        const data = await response.json();
        setEggs(data);
      }
    } catch (err) {
      console.error('Failed to fetch eggs:', err);
    }
  };

  useEffect(() => {
    fetchEggs();
    const interval = setInterval(fetchEggs, 10000);
    return () => clearInterval(interval);
  }, [sessionToken]);

  const handlePullEgg = async () => {
    if (!sessionToken) return;
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/eggs/pull`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (response.ok) {
        const egg = await response.json();
        setMessage(`🥚 A ${egg.rarity} egg has arrived!`);
        await fetchEggs();
      } else {
        const err = await response.json();
        setMessage(err.detail || 'Failed to pull egg');
      }
    } catch (err) {
      setMessage('Network error');
    } finally {
      setLoading(false);
    }
  };

  const handleHatch = async (eggUuid: string) => {
    if (!sessionToken) return;
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/eggs/${eggUuid}/hatch`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (response.ok) {
        const companion = await response.json();
        setMessage(`🎉 A ${companion.species} has hatched!`);
        await fetchEggs();
        setSelectedEgg(null);
      } else {
        const err = await response.json();
        setMessage(err.detail || 'Failed to hatch egg');
      }
    } catch (err) {
      setMessage('Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="hatchery-view">
      <div className="hatchery-header">
        <h1>Hatchery</h1>
        <button 
          className="btn-primary pull-egg-btn" 
          onClick={handlePullEgg} 
          disabled={loading}
        >
          {loading ? '...' : 'Pull Egg'}
        </button>
      </div>

      {message && <div className="game-message">{message}</div>}

      <PhaserGame width={800} height={500} />
      
      <div className="egg-shelf">
        {eggs.length === 0 ? (
          <div className="empty-shelf">
            <p>No eggs yet. Pull your first egg to begin!</p>
          </div>
        ) : (
          eggs.map((egg) => (
            <div
              key={egg.uuid}
              className={`egg-card ${selectedEgg === egg.uuid ? 'selected' : ''}`}
              onClick={() => setSelectedEgg(egg.uuid)}
            >
              <div 
                className="egg-visual"
                style={{ 
                  backgroundColor: RARITY_COLORS[egg.rarity] || '#808080',
                  boxShadow: `0 0 20px ${RARITY_COLORS[egg.rarity] || '#808080'}`,
                }}
              />
              <span className="egg-rarity">{egg.rarity}</span>
            </div>
          ))
        )}
      </div>

      {selectedEgg && (
        <div className="incubator-panel">
          <button 
            className="btn-primary hatch-btn"
            onClick={() => handleHatch(selectedEgg)}
            disabled={loading}
          >
            {loading ? 'Hatching...' : 'Hatch Egg'}
          </button>
        </div>
      )}
    </div>
  );
}
