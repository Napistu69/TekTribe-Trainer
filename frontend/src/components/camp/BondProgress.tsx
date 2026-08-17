interface BondProgressProps {
  bondLevel: number;
}

export function BondProgress({ bondLevel }: BondProgressProps) {
  const nextThreshold = bondLevel < 100 ? 100 : bondLevel < 500 ? 500 : 1000;
  const progress = Math.min(100, (bondLevel / nextThreshold) * 100);

  return (
    <div className="bond-progress">
      <div className="bond-header">
        <span className="bond-label">Bond</span>
        <span className="bond-level">{bondLevel} / {nextThreshold}</span>
      </div>
      <div className="bond-bar">
        <div className="bond-fill" style={{ width: `${progress}%` }} />
      </div>
    </div>
  );
}
