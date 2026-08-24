import { useState, useEffect, useRef } from 'react';
import { useAuthStore } from '../stores/authStore';
import { TutorialOverlay, useTutorial } from '../components/shared/TutorialOverlay';

const TUTORIAL_STEPS = [
  { title: 'Training Grounds', text: 'Train your companions in mini-games to improve their stats and earn rewards.' },
  { title: 'Mini-Games', text: 'Each mini-game trains different stats. Choose wisely based on what your companion needs.' },
  { title: 'Cooldowns', text: 'Training has cooldowns. You can train again after the cooldown expires.' },
];

export function TrainingView() {
  const [selectedGame, setSelectedGame] = useState<{id: string; name: string; icon: string; difficulty: string} | null>(null);
  const [training, setTraining] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const { showTutorial, completeTutorial } = useTutorial('tutorial-training');
  const sessionToken = useAuthStore((s) => s.sessionToken);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  const handleTrain = async (gameId: string) => {
    if (!sessionToken || !gameId || training) return;
    setTraining(true);
    setMessage(null);
    try {
      const companionsResp = await fetch(`${import.meta.env.VITE_API_URL}/api/companions`, {
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!companionsResp.ok) {
        if (mountedRef.current) setMessage('Failed to fetch companions');
        if (mountedRef.current) setTraining(false);
        return;
      }
      const companions = await companionsResp.json();
      if (!companions || companions.length === 0) {
        if (mountedRef.current) setMessage('No companions available to train');
        if (mountedRef.current) setTraining(false);
        return;
      }
      const companionUuid = companions[0].uuid;
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/training/submit`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${sessionToken}` },
        body: JSON.stringify({ companion_uuid: companionUuid, game_id: gameId, score: Math.floor(Math.random() * 100), duration_seconds: 30 }),
      });
      if (!mountedRef.current) return;
      if (response.ok) {
        try { const result = await response.json(); if (mountedRef.current) setMessage(`Training complete! +${result.bond_gained} bond, +${result.dust_earned} dust`); } catch { if (mountedRef.current) setMessage('Training complete!'); }
      } else {
        try { const err = await response.json(); if (mountedRef.current) setMessage(err.detail || 'Training failed'); } catch { if (mountedRef.current) setMessage('Training failed'); }
      }
    } catch (err) {
      if (mountedRef.current) setMessage('Network error');
    } finally {
      if (mountedRef.current) setTraining(false);
    }
  };

  const games = [
    { id: 'target_tap', name: 'Target Tap', icon: '🎯', difficulty: 'Easy' },
    { id: 'rhythm_graze', name: 'Rhythm Graze', icon: '🎵', difficulty: 'Very Easy' },
    { id: 'charge_line', name: 'Charge Line', icon: '⚡', difficulty: 'Easy' },
    { id: 'sprint_course', name: 'Sprint Course', icon: '🏃', difficulty: 'Medium' },
    { id: 'sky_glide', name: 'Sky Glide', icon: '🌤️', difficulty: 'Medium' },
    { id: 'alpha_resolve', name: 'Alpha Resolve', icon: '👑', difficulty: 'Hard' },
  ];

  return (
    <div className="training-view">
      {showTutorial && <TutorialOverlay steps={TUTORIAL_STEPS} storageKey="tutorial-training" onComplete={completeTutorial} />}
      <h1>Training</h1>
      {message && <div className="game-message">{message}</div>}
      <div className="minigame-grid">
        {games.map(game => (
          <div key={game.id} className={`minigame-card ${selectedGame?.id === game.id ? 'selected' : ''}`} onClick={() => setSelectedGame(game)}>
            <span className="minigame-icon">{game.icon}</span>
            <h3>{game.name}</h3>
            <span className="difficulty">{game.difficulty}</span>
          </div>
        ))}
      </div>
      {selectedGame && (
        <div className="minigame-detail">
          <h3>{selectedGame.name}</h3>
          <button className="btn-primary train-btn" onClick={() => handleTrain(selectedGame.id)} disabled={training}>
            {training ? 'Training...' : 'Start Training'}
          </button>
        </div>
      )}
    </div>
  );
}
