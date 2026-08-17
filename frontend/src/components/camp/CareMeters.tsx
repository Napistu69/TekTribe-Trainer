interface CareState {
  hunger: number;
  energy: number;
  morale: number;
  cleanliness: number;
}

interface CareMetersProps {
  careState: CareState | null;
}

export function CareMeters({ careState }: CareMetersProps) {
  if (!careState) return <div className="care-meters loading">Loading...</div>;

  const meters = [
    { label: 'Hunger', value: careState.hunger, color: '#00ff88' },
    { label: 'Energy', value: careState.energy, color: '#ffd700' },
    { label: 'Morale', value: careState.morale, color: '#00d4ff' },
    { label: 'Clean', value: careState.cleanliness, color: '#ff88ff' },
  ];

  return (
    <div className="care-meters">
      {meters.map((m) => (
        <div key={m.label} className="meter-row">
          <span className="meter-label">{m.label}</span>
          <div className="meter-bar">
            <div
              className="meter-fill"
              style={{ width: `${m.value * 100}%`, backgroundColor: m.color }}
            />
          </div>
          <span className="meter-value">{Math.round(m.value * 100)}%</span>
        </div>
      ))}
    </div>
  );
}
