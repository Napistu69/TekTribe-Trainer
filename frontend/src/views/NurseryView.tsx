import { useState, useEffect, useRef } from 'react';
import { useAuthStore } from '../stores/authStore';
import { TutorialOverlay, useTutorial } from '../components/shared/TutorialOverlay';

const TUTORIAL_STEPS = [
  { title: 'Welcome to the Nursery', text: 'This is where hatchlings and juveniles are cared for. Feed, clean, imprint, and rest your young companions.' },
  { title: 'Care Actions', text: 'Each care action has a cooldown. Use them wisely to keep your companion healthy and happy.' },
  { title: 'Growth', text: 'As your companion grows, they will eventually become adults and move to the Camp!' },
];

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

export function NurseryView() {
  const [companion, setCompanion] = useState<Companion | null>(null);
  const [selectedCompanion, setSelectedCompanion] = useState<string | null>(null);
  const [companions, setCompanions] = useState<Companion[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const { showTutorial, completeTutorial } = useTutorial('tutorial-nursery');
  const sessionToken = useAuthStore((s) => s.sessionToken);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  const isJuvenileOrHatchling = (c: Companion) => c.life_stage === 'hatchling' || c.life_stage === 'juvenile';

  const fetchCompanions = async () => {
    if (!sessionToken) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/companions`, {
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!response.ok) return;
      const data = await response.json();
      if (!mountedRef.current) return;
      
      const filtered = data.filter(isJuvenileOrHatchling);
      setCompanions(filtered);
      if (filtered.length > 0 && !selectedCompanion) {
        setSelectedCompanion(filtered[0].uuid);
        setCompanion(filtered[0]);
      }
    } catch (err) {
      console.error('Failed to fetch companions:', err);
    }
  };

  useEffect(() => { fetchCompanions(); }, [sessionToken]);

  useEffect(() => {
    if (selectedCompanion) {
      const c = companions.find(c => c.uuid === selectedCompanion);
      if (c) setCompanion(c);
    }
  }, [selectedCompanion, companions]);

  const handleCareAction = async (action: string) => {
    if (!sessionToken || !selectedCompanion || loading) return;
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/care/${selectedCompanion}/${action}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!mountedRef.current) return;
      if (response.ok) {
        setMessage(`${action} successful!`);
        await fetchCompanions();
      } else {
        try { const err = await response.json(); setMessage(err.detail || 'Care action failed'); } catch { setMessage('Care action failed'); }
      }
    } catch (err) {
      if (mountedRef.current) setMessage('Network error');
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  };

  if (!companion) {
    return (
      <div className="nursery-view">
        {showTutorial && <TutorialOverlay steps={TUTORIAL_STEPS} storageKey="tutorial-nursery" onComplete={completeTutorial} />}
        <h1>Nursery</h1>
        <div className="empty-nursery">
          <p>No hatchlings or juveniles yet. Hatch an egg to get started!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="nursery-view">
      {showTutorial && <TutorialOverlay steps={TUTORIAL_STEPS} storageKey="tutorial-nursery" onComplete={completeTutorial} />}
      <h1>Nursery</h1>
      {message && <div className="game-message">{message}</div>}
      <div className="companion-selector">
        {companions.map(c => (
          <button key={c.uuid} className={`companion-tab ${selectedCompanion === c.uuid ? 'active' : ''}`} onClick={() => setSelectedCompanion(c.uuid)}>
            {c.species}
          </button>
        ))}
      </div>
      <div className="companion-display">
        <div className="companion-visual">
          <img src={`/assets/Creatures/${companion.species}_character.png`} alt={companion.species} className="companion-image" />
          <div className="companion-info">
            <h2>{companion.name || companion.species}</h2>
            <span className="life-stage">{companion.life_stage}</span>
          </div>
        </div>
        <div className="care-actions">
          {['feed', 'clean', 'imprint', 'rest'].map(a => (
            <button key={a} className="care-action-btn" onClick={() => handleCareAction(a)} disabled={loading}>
              <span className="care-label">{a}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
