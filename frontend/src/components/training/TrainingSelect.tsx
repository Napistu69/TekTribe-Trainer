interface MiniGameInfo {
  id: string;
  name: string;
  species: string;
  description: string;
  difficulty: string;
  stats: [string, string];
}

const MINI_GAMES: MiniGameInfo[] = [
  { id: 'target_tap', name: 'Target Tap', species: 'Dilo', description: 'Tap targets as they appear', difficulty: 'Easy', stats: ['Focus', 'Trick Skill'] },
  { id: 'rhythm_graze', name: 'Rhythm Graze', species: 'Parasaur', description: 'Tap in rhythm', difficulty: 'Very Easy', stats: ['Trust', 'Affection'] },
  { id: 'sprint_course', name: 'Sprint Course', species: 'Raptor', description: 'Dodge obstacles', difficulty: 'Medium', stats: ['Speed', 'Drive'] },
  { id: 'sky_glide', name: 'Sky Glide', species: 'Ptera', description: 'Glide through rings', difficulty: 'Medium', stats: ['Agility', 'Curiosity'] },
  { id: 'charge_line', name: 'Charge Line', species: 'Trike', description: 'Charge and release', difficulty: 'Easy', stats: ['Grit', 'Defense'] },
  { id: 'alpha_resolve', name: 'Alpha Resolve', species: 'Rex', description: 'Manage your stamina', difficulty: 'Hard', stats: ['Power', 'Discipline'] },
];

interface TrainingSelectProps {
  companionSpecies: string;
  onSelect: (gameId: string) => void;
}

export function TrainingSelect({ companionSpecies, onSelect }: TrainingSelectProps) {
  // Filter games — show species-specific game first, then others
  const speciesGame = MINI_GAMES.find(g => g.species.toLowerCase() === companionSpecies);
  const otherGames = MINI_GAMES.filter(g => g.species.toLowerCase() !== companionSpecies);
  const games = speciesGame ? [speciesGame, ...otherGames] : MINI_GAMES;

  return (
    <div className="training-select">
      <h2>Training Arena</h2>
      <p className="subtitle">Choose a training mini-game</p>
      
      <div className="games-grid">
        {games.map((game) => (
          <button
            key={game.id}
            className={`game-card ${game.species.toLowerCase() === companionSpecies ? 'recommended' : ''}`}
            onClick={() => onSelect(game.id)}
          >
            <div className="game-card-header">
              <span className="game-name">{game.name}</span>
              {game.species.toLowerCase() === companionSpecies && (
                <span className="recommended-badge">Best for {game.species}</span>
              )}
            </div>
            <p className="game-description">{game.description}</p>
            <div className="game-meta">
              <span className="difficulty">{game.difficulty}</span>
              <span className="stats">{game.stats.join(' + ')}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
