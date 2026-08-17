import { useEconomyStore } from '../../stores/economyStore';

interface BalanceDisplayProps {
  compact?: boolean;
}

export function BalanceDisplay({ compact = false }: BalanceDisplayProps) {
  const dust = useEconomyStore((s) => s.dust);
  
  if (compact) {
    return (
      <div className="balance-display compact">
        <span className="dust-icon">✦</span>
        <span className="dust-value">{dust}</span>
      </div>
    );
  }
  
  return (
    <div className="balance-display">
      <div className="balance-item">
        <span className="currency-icon dust">✦</span>
        <span className="currency-label">Dust</span>
        <span className="currency-value">{dust}</span>
      </div>
    </div>
  );
}
