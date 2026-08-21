import { useState } from 'react';
import { useAuthStore } from '../stores/authStore';

interface MiniGame {
  id: string;
  name: string;
  description: string;
  icon: string;
  difficulty: string;
  trains: string[];
}

const SPECIES_MINIGAMES: MiniGame[] = [
  { id: 'target_tap', name: 'Target Tap', description: 'Tap the targets as they appear!', icon: '🎯', difficulty: 'Easy', trains: ['Focus', 'Trick Skill'] },
  { id: 'rhythm_graze', name: 'Rhythm Graze', description: 'Tap to the rhythm of nature', icon: '🎵', difficulty: 'Very Easy', trains: ['Trust', 'Affection'] },
  { id: 'charge_line', name: 'Charge Line', description: 'Hold and release at the right moment!', icon: '⚡', difficulty: 'Easy', trains: ['Grit', 'Defense'] },
  { id: 'sprint_course', name: 'Sprint Course', description: 'Swipe to jump over obstacles!', icon: '🏃', difficulty: 'Medium', trains: ['Speed', 'Drive'] },
  { id: 'sky_glide', name: 'Sky Glide', description: 'Balance through the clouds', icon: '🌤️', difficulty: 'Medium', trains: ['Agility', 'Curiosity'] },
  { id: 'alpha_resolve', name: 'Alpha Resolve', description: 'Master your stamina to win', icon: '👑', difficulty: 'Hard', trains: ['Power', 'Discipline'] },
];

const UNLOCKED_MINIGAMES: MiniGame[] = [
  { id: 'chase_drills', name: 'Chase Drills', description: 'Swipe lanes to catch prey', icon: '🦴', difficulty: 'Medium', trains: ['Speed'] },
  { id: 'balance_crossing', name: 'Balance Crossing', description: 'Tilt to maintain balance', icon: '⚖️', difficulty: 'Medium', trains: ['Temperament', 'Awareness'] },
  { id: 'roar_timing', name: 'Roar Timing', description: 'Tap at the pulse rings', icon: '🔊', difficulty: 'Easy', trains: ['Strength', 'Morale'] },
];

const DIFFICULTY_COLORS: Record<string, string> = {
  'Very Easy': '#00ff00',
  'Easy': '#80ff00',
  'Medium': '#ffff00',
  'Hard': '#ff8000',
};

export function TrainingView() {
  const [selectedGame, setSelectedGame] = useState<MiniGame | null>(null);
  const [training, setTraining] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const sessionToken = useAuthStore((s) => s.sessionToken);

  const handleTrain = async (gameId: string) => {
    if (!sessionToken) return;
    setTraining(true);
    setMessage(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/training/submit`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${sessionToken}` },
        body: JSON.stringify({ minigame_id: gameId, score: Math.floor(Math.random() * 100) }),
      });
      if (response.ok) {
        const result = await response.json();
        setMessage(`Training complete! +${result.bond_gained} bond, +${result.dust_earned} dust`);
      } else {
        const err = await response.json();
        setMessage(err.detail || 'Training failed');
      }
    } catch (err) {
      setMessage('Network error');
    } finally {
      setTraining(false);
    }
  };

  const allGames = [...SPECIES_MINIGAMES, ...UNLOCKED_MINIGAMES];

  return (
    <div className="training-view">
      <h1>Training</h1>

      {message && <div className="game-message">{message}</div>}

      <div className="minigame-grid">
        {allGames.map(game => (
          <div
            key={game.id}
            className={`minigame-card ${selectedGame?.id === game.id ? 'selected' : ''}`}
            onClick={() => setSelectedGame(game)}
          >
            <span className="minigame-icon">{game.icon}</span>
            <h3>{game.name}</h3>
            <span className="difficulty" style={{ color: DIFFICULTY_COLORS[game.difficulty] }}>
              {game.difficulty}
            </span>
          </div>
        ))}
      </div>

      {selectedGame && (
        <div className="minigame-detail">
          <h3>{selectedGame.name}</h3>
          <p>{selectedGame.description}</p>
          <div className="trains-list">
            <span>Trains:</span>
            {selectedGame.trains.map(t => (
              <span key={t} className="train-tag">{t}</span>
            ))}
          </div>
          <button
            className="btn-primary train-btn"
            onClick={() => handleTrain(selectedGame.id)}
            disabled={training}
          >
            {training ? 'Training...' : 'Start Training'}
          </button>
        </div>
      )}
    </div>
  );
}
