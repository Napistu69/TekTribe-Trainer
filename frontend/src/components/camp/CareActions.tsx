interface CareActionsProps {
  onAction: (action: string) => void;
  disabled: boolean;
}

const ACTIONS = [
  { id: 'feed', label: 'Feed', icon: '🌿' },
  { id: 'clean', label: 'Clean', icon: '🧼' },
  { id: 'reassure', label: 'Reassure', icon: '💬' },
  { id: 'rest', label: 'Rest', icon: '💤' },
  { id: 'observe', label: 'Observe', icon: '👁' },
];

export function CareActions({ onAction, disabled }: CareActionsProps) {
  return (
    <div className="care-actions">
      {ACTIONS.map((a) => (
        <button
          key={a.id}
          className="action-btn"
          onClick={() => onAction(a.id)}
          disabled={disabled}
        >
          <span className="action-icon">{a.icon}</span>
          <span className="action-label">{a.label}</span>
        </button>
      ))}
    </div>
  );
}
