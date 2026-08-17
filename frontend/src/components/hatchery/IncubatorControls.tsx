interface Egg {
  uuid: string;
  rarity: string;
  source: string;
  pulled_at: string;
  incubation_started_at: string | null;
  temperature: number;
  stability: number;
}

interface IncubatorControlsProps {
  egg: Egg | undefined;
}

export function IncubatorControls({ egg }: IncubatorControlsProps) {
  if (!egg) return null;
  
  return (
    <div className="incubator-controls">
      <h3>Incubator</h3>
      <div className="control-row">
        <label>Temperature</label>
        <div className="meter">
          <div className="meter-fill" style={{ width: `${egg.temperature * 100}%` }} />
        </div>
        <span>{Math.round(egg.temperature * 100)}%</span>
      </div>
      <div className="control-row">
        <label>Stability</label>
        <div className="meter">
          <div className="meter-fill" style={{ width: `${egg.stability * 100}%` }} />
        </div>
        <span>{Math.round(egg.stability * 100)}%</span>
      </div>
    </div>
  );
}
