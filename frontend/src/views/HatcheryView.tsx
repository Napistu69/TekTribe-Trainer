import { useState, useEffect, useRef } from 'react';
import { useAuthStore } from '../stores/authStore';
import { TutorialOverlay, useTutorial } from '../components/shared/TutorialOverlay';

const TUTORIAL_STEPS = [
  { title: 'Welcome to the Hatchery', text: 'Your journey begins with a single egg. Pull your first egg to start!' },
  { title: 'Incubation', text: 'Eggs need warmth and time. Keep them incubated until they\'re ready to hatch!' },
  { title: 'Hatching', text: 'Once incubation is complete, hatch your egg to reveal your companion!' },
  { title: 'Care & Training', text: 'Feed, clean, and train your companion to grow stronger together.' },
];

const RARITY_IMAGES: Record<string, string> = {
  common: '/assets/Hatch System/Egg_Common.png',
  uncommon: '/assets/Hatch System/Egg_Uncommon.png',
  rare: '/assets/Hatch System/Egg_Rare.png',
  epic: '/assets/Hatch System/Egg_Epic.png',
  ascendant: '/assets/Hatch System/Egg_Ascendant.png',
  legendary: '/assets/Hatch System/Egg_Legendary.png',
  mythic: '/assets/Hatch System/Egg_Mythic.png',
};

const RARITY_COLORS: Record<string, string> = {
  common: '#808080',      // grey
  uncommon: '#00ff00',    // Natural green
  rare: '#00d4ff',        // Tier 2 cyan
  epic: '#00ff88',        // Tier 2 emerald (Zero Point)
  ascendant: '#4a9b8f',   // Tier 2 patina copper
  legendary: '#d4a84b',   // Tier 2 gold
  mythic: '#ff4444',      // Natural red (positive terminal)
};

export function HatcheryView() {
  const [eggs, setEggs] = useState<any[]>([]);
  const [selectedEgg, setSelectedEgg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const { showTutorial, completeTutorial } = useTutorial('tutorial-hatchery');
  const sessionToken = useAuthStore((s) => s.sessionToken);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  const fetchEggs = async () => {
    if (!sessionToken) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/eggs`, {
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!response.ok) return;
      const data = await response.json();
      if (mountedRef.current) setEggs(data);
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
    if (!sessionToken || loading) return;
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/eggs/pull`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!mountedRef.current) return;
      if (response.ok) {
        try { const egg = await response.json(); if (mountedRef.current) setMessage(`A ${egg.rarity} egg has arrived!`); await fetchEggs(); } catch { if (mountedRef.current) setMessage('Egg pulled!'); }
      } else {
        try { const err = await response.json(); if (mountedRef.current) setMessage(err.detail || 'Failed to pull egg'); } catch { if (mountedRef.current) setMessage('Failed to pull egg'); }
      }
    } catch (err) {
      if (mountedRef.current) setMessage('Network error');
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  };

  const handleHatch = async (eggUuid: string) => {
    if (!sessionToken || loading) return;
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/eggs/${eggUuid}/hatch`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!mountedRef.current) return;
      if (response.ok) {
        try { const companion = await response.json(); if (mountedRef.current) setMessage(`A ${companion.species} has hatched!`); await fetchEggs(); if (mountedRef.current) setSelectedEgg(null); } catch { if (mountedRef.current) { setMessage('Companion hatched!'); setSelectedEgg(null); } }
      } else {
        try { const err = await response.json(); if (mountedRef.current) setMessage(err.detail || 'Failed to hatch egg'); } catch { if (mountedRef.current) setMessage('Failed to hatch egg'); }
      }
    } catch (err) {
      if (mountedRef.current) setMessage('Network error');
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  };

  const selected = eggs.find(e => e.uuid === selectedEgg);

  return (
    <div className="hatchery-view">
      {showTutorial && <TutorialOverlay steps={TUTORIAL_STEPS} storageKey="tutorial-hatchery" onComplete={completeTutorial} />}
      <div className="hatchery-header">
        <h1>Hatchery</h1>
        <button className="btn-primary pull-egg-btn" onClick={handlePullEgg} disabled={loading}>
          {loading ? '...' : 'Pull Egg'}
        </button>
      </div>
      {message && <div className="game-message">{message}</div>}
      <div className="egg-shelf">
        {eggs.length === 0 ? (
          <div className="empty-shelf"><p>No eggs yet. Pull your first egg to begin!</p></div>
        ) : (
          eggs.map((egg) => (
            <div
              key={egg.uuid}
              className={`egg-card ${selectedEgg === egg.uuid ? 'selected' : ''}`}
              onClick={() => setSelectedEgg(egg.uuid)}
              style={{ borderColor: selectedEgg === egg.uuid ? RARITY_COLORS[egg.rarity] : undefined }}
            >
              <img
                src={RARITY_IMAGES[egg.rarity] || RARITY_IMAGES.common}
                alt={egg.rarity}
                className="egg-visual"
                style={{ filter: `drop-shadow(0 0 10px ${RARITY_COLORS[egg.rarity]})` }}
              />
              <span className="egg-rarity" style={{ color: RARITY_COLORS[egg.rarity] }}>{egg.rarity}</span>
            </div>
          ))
        )}
      </div>
      {selected && (
        <div id="incubator" className="incubator-panel">
          <h3>Incubator</h3>
          <div className="incubator-egg">
            <img
              src={RARITY_IMAGES[selected.rarity] || RARITY_IMAGES.common}
              alt="Egg"
              className="egg-visual large"
              style={{ filter: `drop-shadow(0 0 20px ${RARITY_COLORS[selected.rarity]})` }}
            />
            <p className="incubator-rarity" style={{ color: RARITY_COLORS[selected.rarity] }}>
              {selected.rarity.toUpperCase()}
            </p>
          </div>
          <button className="btn-primary hatch-btn" onClick={() => handleHatch(selected.uuid)} disabled={loading}>
            {loading ? 'Hatching...' : 'Hatch Egg'}
          </button>
        </div>
      )}
    </div>
  );
}
