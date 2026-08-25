import { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useEconomyStore } from '../stores/economyStore';

interface ShopItem {
  item_id: string;
  name: string;
  description: string;
  cost: number;
  effect: any;
  category: string;
}

interface EconomyViewProps {
  companionUuid?: string;
}

export function EconomyView({ companionUuid }: EconomyViewProps) {
  const [items, setItems] = useState<ShopItem[]>([]);
  const [purchasing, setPurchasing] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [tab, setTab] = useState<'shop' | 'history'>('shop');
  const sessionToken = useAuthStore((s) => s.sessionToken);
  const dust = useEconomyStore((s) => s.dust);
  const setBalance = useEconomyStore((s) => s.setBalance);

  useEffect(() => {
    if (!sessionToken) return;
    const fetchShopItems = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/economy/shop`);
        if (response.ok) {
          const data = await response.json();
          setItems(data);
        }
      } catch (err) {
        console.error('Failed to fetch shop items:', err);
      }
    };
    fetchShopItems();
  }, [sessionToken]);

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
  }, [sessionToken, setBalance]);

  const handlePurchase = async (itemId: string) => {
    if (!sessionToken) return;
    setPurchasing(itemId);
    setMessage(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/economy/shop/purchase`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${sessionToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ item_id: itemId, companion_uuid: companionUuid || null }),
      });
      if (response.ok) {
        const purchaseResult = await response.json();
        setMessage(`Purchased ${items.find(i => i.item_id === itemId)?.name}!`);
        console.log('Purchase result:', purchaseResult);
        const balanceRes = await fetch(`${import.meta.env.VITE_API_URL}/api/economy/balance`, {
          headers: { Authorization: `Bearer ${sessionToken}` },
        });
        if (balanceRes.ok) {
          const balanceData = await balanceRes.json();
          setBalance(balanceData);
        }
      } else {
        const err = await response.json();
        setMessage(err.detail || 'Purchase failed');
      }
    } catch (err) {
      setMessage('Network error');
    } finally {
      setPurchasing(null);
    }
  };

  return (
    <div className="economy-view">
      <h1>Economy</h1>
      
      <div className="economy-tabs">
        <button className={`tab ${tab === 'shop' ? 'active' : ''}`} onClick={() => setTab('shop')}>Shop</button>
        <button className={`tab ${tab === 'history' ? 'active' : ''}`} onClick={() => setTab('history')}>History</button>
      </div>

      {message && <div className="game-message">{message}</div>}

      {tab === 'shop' && (
        <div className="shop-items">
          {items.map((item) => (
            <div key={item.item_id} className="shop-item">
              <div className="item-info">
                <span className="item-name">{item.name}</span>
                <span className="item-description">{item.description}</span>
              </div>
              <div className="item-purchase">
                <span className="item-cost">✦ {item.cost}</span>
                <button
                  className="btn-small"
                  onClick={() => handlePurchase(item.item_id)}
                  disabled={dust < item.cost || purchasing === item.item_id}
                >
                  {purchasing === item.item_id ? '...' : 'Buy'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === 'history' && (
        <div className="history-panel">
          <TransactionHistory />
        </div>
      )}
    </div>
  );
}

function TransactionHistory() {
  const [transactions, setTransactions] = useState<any[]>([]);
  const sessionToken = useAuthStore((s) => s.sessionToken);

  useEffect(() => {
    if (!sessionToken) return;
    const fetchHistory = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/economy/history`, {
          headers: { Authorization: `Bearer ${sessionToken}` },
        });
        if (response.ok) {
          const data = await response.json();
          setTransactions(data.transactions || []);
        }
      } catch (err) {
        console.error('Failed to fetch history:', err);
      }
    };
    fetchHistory();
  }, [sessionToken]);

  if (transactions.length === 0) {
    return <p className="empty-history">No transactions yet.</p>;
  }

  return (
    <div className="transaction-list">
      {transactions.map((tx, i) => (
        <div key={i} className="transaction-row">
          <span className={`tx-type ${tx.type}`}>{tx.type}</span>
          <span className="tx-currency">{tx.currency}</span>
          <span className={`tx-amount ${tx.type === 'award' ? 'positive' : 'negative'}`}>
            {tx.type === 'award' ? '+' : '-'}{tx.amount}
          </span>
          <span className="tx-source">{tx.source || tx.sink}</span>
        </div>
      ))}
    </div>
  );
}
