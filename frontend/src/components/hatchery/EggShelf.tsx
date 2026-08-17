interface Egg {
  uuid: string;
  rarity: string;
  source: string;
  pulled_at: string;
  incubation_started_at: string | null;
  temperature: number;
  stability: number;
}

interface EggShelfProps {
  eggs: Egg[];
  selectedEgg: string | null;
  onSelectEgg: (uuid: string) => void;
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

export function EggShelf({ eggs, selectedEgg, onSelectEgg }: EggShelfProps) {
  if (eggs.length === 0) {
    return (
      <div className="egg-shelf empty">
        <p>No eggs yet. Pull your first egg to begin!</p>
      </div>
    );
  }

  return (
    <div className="egg-shelf">
      {eggs.map((egg) => (
        <div
          key={egg.uuid}
          className={`egg-card ${selectedEgg === egg.uuid ? 'selected' : ''}`}
          onClick={() => onSelectEgg(egg.uuid)}
        >
          <div
            className="egg-visual"
            style={{ backgroundColor: RARITY_COLORS[egg.rarity] || '#808080' }}
          />
          <span className="egg-rarity">{egg.rarity}</span>
        </div>
      ))}
    </div>
  );
}
