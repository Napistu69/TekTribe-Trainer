import { useState, useEffect } from 'react';
import { useEconomyStore } from '../../stores/economyStore';
import { useAuthStore } from '../../stores/authStore';

interface WalletModalProps {
  onClose: () => void;
}

type WalletTab = 'currencies' | 'inventory' | 'history';

interface InventoryItem {
  item_id: string;
  name: string;
  description: string;
  quantity: number;
}

const ITEM_ICONS: Record<string, string> = {
  meat: '🥩',
  jerky: '🥓',
  berries: '🍒',
  crops: '🥕',
  sponge: '🧽',
  imprint_elixir: '🧪',
  care_kit: '🧰',
};

export function WalletModal({ onClose }: WalletModalProps) {
  const [activeTab, setActiveTab] = useState<WalletTab>('currencies');
  const dust = useEconomyStore((s) => s.dust);
  const shard = useEconomyStore((s) => s.shard);
  const cuboid = useEconomyStore((s) => s.cuboid);
  const ele = useEconomyStore((s) => s.ele);
  const transactions = useEconomyStore((s) => s.transactions);
  const setBalance = useEconomyStore((s) => s.setBalance);
  const setTransactions = useEconomyStore((s) => s.setTransactions);
  const sessionToken = useAuthStore((s) => s.sessionToken);
  const [inventory, setInventory] = useState<InventoryItem[]>([]);

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

  useEffect(() => {
    if (!sessionToken || activeTab !== 'history') return;
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
  }, [sessionToken, activeTab]);

  useEffect(() => {
    if (!sessionToken) return;
    const fetchInventory = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/inventory`, {
          headers: { Authorization: `Bearer ${sessionToken}` },
        });
        if (response.ok) {
          const data = await response.json();
          setInventory(data.items || []);
        }
      } catch (err) {
        console.error('Failed to fetch inventory:', err);
      }
    };
    fetchInventory();
  }, [sessionToken]);

  return (
    <div className="wallet-overlay" onClick={onClose}>
      <div className="wallet-modal" onClick={(e) => e.stopPropagation()}>
        <div className="wallet-header">
          <h2>Wallet</h2>
          <button className="wallet-close" onClick={onClose}>✕</button>
        </div>

        <div className="wallet-tabs">
          <button
            className={`wallet-tab ${activeTab === 'currencies' ? 'active' : ''}`}
            onClick={() => setActiveTab('currencies')}
          >
            Currencies
          </button>
          <button
            className={`wallet-tab ${activeTab === 'inventory' ? 'active' : ''}`}
            onClick={() => setActiveTab('inventory')}
          >
            Inventory
          </button>
          <button
            className={`wallet-tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            History
          </button>
        </div>

        <div className="wallet-content">
          {activeTab === 'currencies' && (
            <div className="currency-grid">
              <div className="currency-card dust">
                <img className="currency-icon" src="/assets/Currency & Resource/ELE_Dust_48.png" alt="Dust" />
                <span className="currency-name">Dust</span>
                <span className="currency-value">{dust.toLocaleString()}</span>
              </div>
              <div className="currency-card shard">
                <img className="currency-icon" src="/assets/Currency & Resource/ELE_Shard_48.png" alt="Shards" />
                <span className="currency-name">Shards</span>
                <span className="currency-value">{shard.toLocaleString()}</span>
              </div>
              <div className="currency-card cuboid">
                <img className="currency-icon" src="/assets/Currency & Resource/ELE_Cuboid_48.png" alt="Cuboids" />
                <span className="currency-name">Cuboids</span>
                <span className="currency-value">{cuboid.toLocaleString()}</span>
              </div>
              <div className="currency-card ele">
                <span className="currency-icon">⚡</span>
                <span className="currency-name">ELE</span>
                <span className="currency-value">{ele.toLocaleString()}</span>
              </div>
            </div>
          )}

          {activeTab === 'inventory' && (
            <div className="inventory-grid">
              {inventory.length === 0 ? (
                <p className="empty-history">No items yet. Visit the Trading Post to buy items!</p>
              ) : (
                inventory.map((item) => (
                  <div key={item.item_id} className="inventory-item">
                    <span className="item-icon">{ITEM_ICONS[item.item_id] || '📦'}</span>
                    <span className="item-name">{item.name}</span>
                    <span className="item-count">×{item.quantity}</span>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'history' && (
            <div className="history-list">
              {transactions.length === 0 ? (
                <p className="empty-history">No transactions yet.</p>
              ) : (
                transactions.map((tx: any, i: number) => (
                  <div key={i} className="history-row">
                    <span className={`tx-type ${tx.type}`}>{tx.type === 'award' ? '+' : '-'}{tx.amount}</span>
                    <span className="tx-currency">{tx.currency}</span>
                    <span className="tx-source">{tx.source || tx.sink}</span>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
