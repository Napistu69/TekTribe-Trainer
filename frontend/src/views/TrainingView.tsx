import { useState, useEffect, useRef } from 'react';
import { useAuthStore } from '../stores/authStore';
import { TutorialOverlay, useTutorial } from '../components/shared/TutorialOverlay';
import { MiniGameCanvas } from '../components/MiniGameCanvas';

const TUTORIAL_STEPS = [
  { title: 'Training Grounds', text: 'Train your companions in mini-games to improve their stats and earn rewards.' },
  { title: 'Mini-Games', text: 'Each mini-game trains different stats. Choose wisely based on what your companion needs.' },
  { title: 'Cooldowns', text: 'Training has cooldowns. You can train again after the cooldown expires.' },
];

const GAME_DURATIONS: Record<string, number> = {
  target_tap: 30,
  rhythm_graze: 30,
  charge_line: 30,
  sprint_course: 45,
  sky_glide: 45,
  alpha_resolve: 60,
};

export function TrainingView() {
  const [selectedGame, setSelectedGame] = useState<{id: string; name: string; icon: string; difficulty: string} | null>(null);
  const [companionUuid, setCompanionUuid] = useState<string | null>(null);
  const [training, setTraining] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const { showTutorial, completeTutorial } = useTutorial('tutorial-training');
  const sessionToken = useAuthStore((s) => s.sessionToken);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  // Fetch the first companion on mount
  useEffect(() => {
    if (!sessionToken) return;
    void fetch(`${import.meta.env.VITE_API_URL}/api/companions`, {
      headers: { Authorization: `Bearer ${sessionToken}` },
    })
      .then(r => r.json())
      .then((data: Array<{uuid: string; name?: string; species: string}>) => {
        if (mountedRef.current) {
          setCompanionUuid(data[0]?.uuid || null);
        }
      })
      .catch(() => {
        if (mountedRef.current) setMessage('Failed to fetch companions');
      });
  }, [sessionToken]);

  const handleGameComplete = (score: number) => {
    if (!mountedRef.current) return;
    setPlaying(false);
    setTraining(false);
    setMessage(`Training complete! Score: ${score}/100`);
  };

  const startGame = () => {
    if (!selectedGame || training || !sessionToken || !companionUuid) return;
    setPlaying(true);
    setTraining(true);
    setMessage(null);
  };

  const cancelGame = () => {
    setPlaying(false);
    setTraining(false);
    setMessage(null);
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
          {playing ? (
            <>
              <MiniGameCanvas
                gameId={selectedGame.id}
                gameName={selectedGame.name}
                difficulty={selectedGame.difficulty}
                duration={GAME_DURATIONS[selectedGame.id] || 30}
                companionUuid={companionUuid || ''}
                onGameComplete={handleGameComplete}
                onCancel={cancelGame}
              />
              <button className="btn-secondary" onClick={cancelGame}>
                Cancel
              </button>
            </>
          ) : (
            <button className="btn-primary train-btn" onClick={startGame} disabled={training || !sessionToken}>
              {training ? 'Starting...' : 'Start Training'}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
