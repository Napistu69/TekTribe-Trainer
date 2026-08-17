interface ExpeditionResultProps {
  result: any;
  onClose: () => void;
}

export function ExpeditionResult({ result, onClose }: ExpeditionResultProps) {
  if (!result) return null;
  
  return (
    <div className="expedition-result-overlay">
      <div className="expedition-result-card">
        <h2>{result.success ? '🎉 Expedition Success!' : '😔 Expedition Failed'}</h2>
        
        <p className="story">{result.encounter_story}</p>
        
        <div className="rewards">
          <div className="reward">
            <span className="reward-label">Dust</span>
            <span className="reward-value">+{result.dust_gained}</span>
          </div>
          <div className="reward">
            <span className="reward-label">Bond</span>
            <span className={`reward-value ${result.bond_change >= 0 ? 'positive' : 'negative'}`}>
              {result.bond_change >= 0 ? '+' : ''}{result.bond_change}
            </span>
          </div>
          {result.oracle_fragment_found && (
            <div className="reward special">
              <span className="reward-label">🔮 Oracle Fragment</span>
              <span className="reward-value">Found!</span>
            </div>
          )}
          {result.companion_injured && (
            <div className="reward injury">
              <span className="reward-label">🩹 Injured</span>
              <span className="reward-value">-30% HP</span>
            </div>
          )}
        </div>
        
        <button className="btn-primary" onClick={onClose}>
          Continue
        </button>
      </div>
    </div>
  );
}
