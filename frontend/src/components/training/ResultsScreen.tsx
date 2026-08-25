import { useTrainingStore } from '../../stores/trainingStore';

interface ResultsScreenProps {
  onPlayAgain: () => void;
  onExit: () => void;
}

export function ResultsScreen({ onPlayAgain, onExit }: ResultsScreenProps) {
  const lastResult = useTrainingStore((s) => s.lastResult);
  const lastScore = useTrainingStore((s) => s.lastScore);

  if (!lastResult) return null;

  const getGrade = (score: number): string => {
    if (score >= 90) return 'S';
    if (score >= 80) return 'A';
    if (score >= 60) return 'B';
    if (score >= 40) return 'C';
    return 'D';
  };

  return (
    <div className="results-screen">
      <div className="results-card">
        <h2>Training Complete!</h2>
        
        <div className="score-display">
          <span className="grade">{getGrade(lastScore || 0)}</span>
          <span className="score-value">{lastScore}/100</span>
        </div>

        <div className="gains-list">
          <div className="gain-item">
            <span className="gain-label">Imprint</span>
            <span className="gain-value">+{lastResult.imprintGained}</span>
          </div>
          {Object.entries(lastResult.statGains).map(([stat, value]) => (
            <div className="gain-item" key={stat}>
              <span className="gain-label">{stat}</span>
              <span className="gain-value">+{value}</span>
            </div>
          ))}
          {lastResult.dustEarned > 0 && (
            <div className="gain-item dust">
              <span className="gain-label">Dust</span>
              <span className="gain-value">+{lastResult.dustEarned}</span>
            </div>
          )}
        </div>

        <div className="results-actions">
          <button className="btn-primary" onClick={onPlayAgain}>
            Play Again
          </button>
          <button className="btn-secondary" onClick={onExit}>
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
