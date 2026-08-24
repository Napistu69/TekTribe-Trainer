import { useState, useEffect, useRef } from 'react';
import { useAuthStore } from '../stores/authStore';
import { TutorialOverlay, useTutorial } from '../components/shared/TutorialOverlay';

const TUTORIAL_STEPS = [
  { title: 'Welcome to the Camp', text: 'This is where adult and elder companions reside. They can be cared for here just like in the Nursery.' },
  { title: 'Camp Background', text: 'Your companion is displayed on the camp background. Watch them bounce gently as they enjoy their home.' },
  { title: 'Unlocking the Camp', text: 'The Camp unlocks when you raise a companion to adulthood through care and training.' },
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

export function CampView() {
  const [companion, setCompanion] = useState<Companion | null>(null);
  const [selectedCompanion, setSelectedCompanion] = useState<string | null>(null);
  const [companions, setCompanions] = useState<Companion[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const { showTutorial, completeTutorial } = useTutorial('tutorial-camp');
  const sessionToken = useAuthStore((s) => s.sessionToken);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  const isAdultOrElder = (c: Companion) => c.life_stage === 'adult' || c.life_stage === 'elder';

  const fetchCompanions = async () => {
    if (!sessionToken) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/companions`, {
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!response.ok) return;
      const data = await response.json();
      if (!mountedRef.current) return;
      
      const filtered = data.filter(isAdultOrElder);
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
      <div className="camp-view">
        {showTutorial && <TutorialOverlay steps={TUTORIAL_STEPS} storageKey="tutorial-camp" onComplete={completeTutorial} />}
        <h1>Camp</h1>
        <div className="empty-camp">
          <p>No adult companions yet. Raise a companion to adulthood to unlock the camp!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="camp-view">
      {showTutorial && <TutorialOverlay steps={TUTORIAL_STEPS} storageKey="tutorial-camp" onComplete={completeTutorial} />}
      <div className="camp-background">
        <img src="/assets/Habitat & Camp/camp_bg.jpg" alt="Camp" className="camp-bg-image" />
        <div className="camp-dino-stage">
          <img src={`/assets/Creatures/${companion.species}_character.png`} alt={companion.species} className="camp-dino-image" />
        </div>
      </div>
      <div className="camp-info-panel">
        {message && <div className="game-message">{message}</div>}
        <div className="companion-selector">
          {companions.map(c => (
            <button key={c.uuid} className={`companion-tab ${selectedCompanion === c.uuid ? 'active' : ''}`} onClick={() => setSelectedCompanion(c.uuid)}>
              {c.species}
            </button>
          ))}
        </div>
        <div className="companion-info">
          <h2>{companion.name || companion.species}</h2>
          <span className="life-stage">{companion.life_stage}</span>
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
