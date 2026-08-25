interface ImprintProgressProps {
  imprintLevel: number;
}

export function ImprintProgress({ imprintLevel }: ImprintProgressProps) {
  const nextThreshold = imprintLevel < 100 ? 100 : imprintLevel < 500 ? 500 : 1000;
  const progress = Math.min(100, (imprintLevel / nextThreshold) * 100);

  return (
    <div className="imprint-progress">
      <div className="imprint-header">
        <span className="imprint-label">Imprint</span>
        <span className="imprint-level">{imprintLevel} / {nextThreshold}</span>
      </div>
      <div className="imprint-bar">
        <div className="imprint-fill" style={{ width: `${progress}%` }} />
      </div>
    </div>
  );
}
