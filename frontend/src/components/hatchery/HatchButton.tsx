interface Egg {
  uuid: string;
  rarity: string;
  source: string;
  pulled_at: string;
  incubation_started_at: string | null;
  temperature: number;
  stability: number;
}

interface HatchButtonProps {
  egg: Egg | undefined;
  onHatch: () => void;
  loading: boolean;
}

export function HatchButton({ egg, onHatch, loading }: HatchButtonProps) {
  if (!egg) return null;
  
  return (
    <div className="hatch-section">
      <button
        className="btn-primary hatch-btn"
        onClick={onHatch}
        disabled={loading}
      >
        {loading ? 'Hatching...' : 'Hatch Egg'}
      </button>
    </div>
  );
}
