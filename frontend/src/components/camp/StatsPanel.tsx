interface Companion {
  base_stats: Record<string, number>;
  mutated_stats: Record<string, number>;
}

interface StatsPanelProps {
  companion: Companion;
}

export function StatsPanel({ companion }: StatsPanelProps) {
  const stats = Object.entries(companion.base_stats);

  return (
    <div className="stats-panel">
      <h4>Stats</h4>
      {stats.map(([key, value]) => {
        const mutated = companion.mutated_stats[key] || 0;
        return (
          <div key={key} className="stat-row">
            <span className="stat-name">{key}</span>
            <span className="stat-value">
              {value}
              {mutated > 0 && <span className="mutated">+{mutated.toFixed(1)}</span>}
            </span>
          </div>
        );
      })}
    </div>
  );
}
