import { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';

interface Egg {
  uuid: string;
  rarity: string;
  source: string;
  pulled_at: string;
  incubation_started_at: string | null;
  temperature: number;
  stability: number;
}

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
  common: '#808080',
  uncommon: '#00ff00',
  rare: '#0080ff',
  epic: '#ff00ff',
  ascendant: '#00ffff',
  legendary: '#ffd700',
  mythic: '#ff0000',
};

const INCUBATION_TIME_MS = 30000;

function formatTime(ms: number): string {
  const totalSeconds = Math.max(0, Math.floor(ms / 1000));
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function TutorialOverlay({ step, onNext, onSkip }: { step: number; onNext: () => void; onSkip: () => void }) {
  const steps = [
    { title: 'Welcome to TekTribe', text: 'Your journey begins with a single egg. Pull your first egg to start!', target: 'pull-btn' },
    { title: 'Incubation', text: 'Eggs need warmth and time. Keep them incubated until they\'re ready to hatch!', target: 'incubator' },
    { title: 'Hatching', text: 'Once incubation is complete, hatch your egg to reveal your companion!', target: 'hatch-btn' },
    { title: 'Care & Training', text: 'Feed, clean, and train your companion to grow stronger together.', target: 'nav-camp' },
  ];

  const current = steps[step];

  return (
    <div className="tutorial-overlay">
      <div className="tutorial-card">
        <h3>{current.title}</h3>
        <p>{current.text}</p>
        <div className="tutorial-actions">
          <button className="btn-primary" onClick={onNext}>{step < steps.length - 1 ? 'Next' : 'Got it!'}</button>
          <button className="btn-secondary" onClick={onSkip}>Skip</button>
        </div>
        <div className="tutorial-dots">
          {steps.map((_, i) => <span key={i} className={`dot ${i === step ? 'active' : ''}`} />)}
        </div>
      </div>
    </div>
  );
}

export function HatcheryView() {
  const [eggs, setEggs] = useState<Egg[]>([]);
  const [selectedEgg, setSelectedEgg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [tutorialStep, setTutorialStep] = useState(0);
  const [showTutorial, setShowTutorial] = useState(true);
  const [now, setNow] = useState(Date.now());
  const sessionToken = useAuthStore((s) => s.sessionToken);

  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);

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
        setMessage(`A ${egg.rarity} egg has arrived!`);
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
        setMessage(`A ${companion.species} has hatched!`);
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

  const selected = eggs.find(e => e.uuid === selectedEgg);
  const incubationEnd = selected?.incubation_started_at
    ? new Date(selected.incubation_started_at).getTime() + INCUBATION_TIME_MS
    : null;
  const timeRemaining = incubationEnd ? incubationEnd - now : 0;
  const isReady = timeRemaining <= 0;

  return (
    <div className="hatchery-view">
      {showTutorial && (
        <TutorialOverlay
          step={tutorialStep}
          onNext={() => {
            if (tutorialStep < 3) setTutorialStep(tutorialStep + 1);
            else { setShowTutorial(false); localStorage.setItem('tutorial-done', 'true'); }
          }}
          onSkip={() => { setShowTutorial(false); localStorage.setItem('tutorial-done', 'true'); }}
        />
      )}

      <div className="hatchery-header">
        <h1>Hatchery</h1>
        <button
          id="pull-btn"
          className="btn-primary pull-egg-btn"
          onClick={handlePullEgg}
          disabled={loading}
        >
          {loading ? '...' : 'Pull Egg'}
        </button>
      </div>

      {message && <div className="game-message">{message}</div>}

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
              <img
                src={RARITY_IMAGES[egg.rarity] || RARITY_IMAGES.common}
                alt={egg.rarity}
                className="egg-image"
                style={{ filter: `drop-shadow(0 0 10px ${RARITY_COLORS[egg.rarity]})` }}
              />
              <span className="egg-rarity">{egg.rarity}</span>
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
              alt={selected.rarity}
              className="egg-image large"
              style={{ filter: `drop-shadow(0 0 20px ${RARITY_COLORS[selected.rarity]})` }}
            />
            <p className="incubator-rarity">{selected.rarity.toUpperCase()}</p>
          </div>
          <div className="incubator-controls">
            <div className="control-row">
              <label>Temperature</label>
              <div className="meter">
                <div className="meter-fill" style={{ width: `${selected.temperature * 100}%` }} />
              </div>
            </div>
            <div className="control-row">
              <label>Stability</label>
              <div className="meter">
                <div className="meter-fill" style={{ width: `${selected.stability * 100}%` }} />
              </div>
            </div>
            {incubationEnd && (
              <div className="control-row">
                <label>Time Left</label>
                <div className="incubation-timer">
                  {isReady ? 'Ready to hatch!' : formatTime(timeRemaining)}
                </div>
              </div>
            )}
          </div>
          <button
            id="hatch-btn"
            className="btn-primary hatch-btn"
            onClick={() => handleHatch(selected.uuid)}
            disabled={loading || !isReady}
          >
            {loading ? 'Hatching...' : isReady ? 'Hatch Egg' : 'Incubating...'}
          </button>
        </div>
      )}
    </div>
  );
}
