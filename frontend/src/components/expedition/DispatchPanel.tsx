import { useState } from 'react';
import { useExpeditionStore } from '../../stores/expeditionStore';

interface DispatchPanelProps {
  companions: any[];
  onDispatch: (companionUuid: string, biomeZone: string, duration: string) => void;
}

const DURATIONS = [
  { key: '2h', label: 'Short', description: '2 hours' },
  { key: '6h', label: 'Medium', description: '6 hours' },
  { key: '12h', label: 'Long', description: '12 hours' },
  { key: '24h', label: 'Extended', description: '24 hours' },
];

export function DispatchPanel({ companions, onDispatch }: DispatchPanelProps) {
  const { selectedBiome, selectedCompanion, selectedDuration, setSelectedCompanion, setSelectedDuration } = useExpeditionStore();
  const [dispatching, setDispatching] = useState(false);
  
  const availableCompanions = companions.filter(c => c.current_state !== 'on_expedition' && c.health_status >= 0.5);
  
  const handleDispatch = () => {
    if (!selectedCompanion || !selectedBiome) return;
    setDispatching(true);
    onDispatch(selectedCompanion, selectedBiome, selectedDuration);
    setTimeout(() => setDispatching(false), 1000);
  };
  
  return (
    <div className="dispatch-panel">
      <h3>Dispatch Expedition</h3>
      
      <div className="form-group">
        <label>Companion</label>
        <select
          value={selectedCompanion || ''}
          onChange={(e) => setSelectedCompanion(e.target.value || null)}
        >
          <option value="">Select a companion...</option>
          {availableCompanions.map((c) => (
            <option key={c.uuid} value={c.uuid}>
              {c.name || c.species} (HP: {Math.round(c.health_status * 100)}%)
            </option>
          ))}
        </select>
        {availableCompanions.length === 0 && (
          <p className="hint">No companions available (all on expedition or injured)</p>
        )}
      </div>
      
      <div className="form-group">
        <label>Duration</label>
        <div className="duration-buttons">
          {DURATIONS.map((d) => (
            <button
              key={d.key}
              className={`duration-btn ${selectedDuration === d.key ? 'selected' : ''}`}
              onClick={() => setSelectedDuration(d.key)}
            >
              <span className="duration-label">{d.label}</span>
              <span className="duration-desc">{d.description}</span>
            </button>
          ))}
        </div>
      </div>
      
      <button
        className="btn-primary dispatch-btn"
        onClick={handleDispatch}
        disabled={!selectedCompanion || !selectedBiome || dispatching}
      >
        {dispatching ? 'Dispatching...' : 'Dispatch'}
      </button>
    </div>
  );
}
