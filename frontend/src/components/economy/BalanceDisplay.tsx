import { useEffect } from 'react';
import { useEconomyStore } from '../../stores/economyStore';
import { useAuthStore } from '../../stores/authStore';

interface BalanceDisplayProps {
  compact?: boolean;
}

export function BalanceDisplay({ compact = false }: BalanceDisplayProps) {
  const dust = useEconomyStore((s) => s.dust);
  const shard = useEconomyStore((s) => s.shard);
  const sessionToken = useAuthStore((s) => s.sessionToken);
  const setBalance = useEconomyStore((s) => s.setBalance);

  useEffect(() => {
    if (!sessionToken) return;
    const fetchBalance = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/economy/balance`, {
          headers: { Authorization: `Bearer ${sessionToken}` },
        });
        if (response.ok) {
          const data = await response.json();
          setBalance(data);
        }
      } catch (err) {
        console.error('Failed to fetch balance:', err);
      }
    };
    fetchBalance();
    const interval = setInterval(fetchBalance, 30000);
    return () => clearInterval(interval);
  }, [sessionToken, setBalance]);

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
      {shard > 0 && (
        <div className="balance-item">
          <span className="currency-icon shard">◆</span>
          <span className="currency-label">Shard</span>
          <span className="currency-value">{shard}</span>
        </div>
      )}
    </div>
  );
}
