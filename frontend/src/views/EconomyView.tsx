import { useState, useEffect, useRef } from 'react';
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

interface EggOffering {
  rarity: string;
  cost: number;
  currency: string;
  daily_stock: number;
  upgrade_chance: number;
}

const ITEM_ICONS: Record<string, string> = {
  meat: '/assets/Hatch System/Egg_Common.png',
  jerky: '/assets/Hatch System/Egg_Common.png',
  berries: '/assets/Hatch System/Egg_Common.png',
  crops: '/assets/Hatch System/Egg_Common.png',
  sponge: '/assets/Hatch System/Egg_Common.png',
  imprint_boost: '/assets/Hatch System/Egg_Common.png',
  care_kit: '/assets/Hatch System/Egg_Common.png',
};

const EGG_IMAGES: Record<string, string> = {
  common: '/assets/Hatch System/Egg_Common.png',
  uncommon: '/assets/Hatch System/Egg_Uncommon.png',
  rare: '/assets/Hatch System/Egg_Rare.png',
  epic: '/assets/Hatch System/Egg_Epic.png',
  ascendant: '/assets/Hatch System/Egg_Ascendant.png',
  legendary: '/assets/Hatch System/Egg_Legendary.png',
  mythic: '/assets/Hatch System/Egg_Mythic.png',
};

const RARITY_COLORS: Record<string, string> = {
  common: '#808080',
  uncommon: '#00ff00',
  rare: '#00d4ff',
  epic: '#ff00ff',
};

interface EconomyViewProps {
  companionUuid?: string;
}

export function EconomyView(_companionUuid?: EconomyViewProps) {
  const [items, setItems] = useState<ShopItem[]>([]);
  const [eggOfferings, setEggOfferings] = useState<EggOffering[]>([]);
  const [purchasing, setPurchasing] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [tab, setTab] = useState<'shop' | 'eggs' | 'history'>('shop');
  const sessionToken = useAuthStore((s) => s.sessionToken);
  const dust = useEconomyStore((s) => s.dust);
  const shard = useEconomyStore((s) => s.shard);
  const setBalance = useEconomyStore((s) => s.setBalance);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  useEffect(() => {
    if (!sessionToken) return;
    const fetchShopItems = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/economy/shop`);
        if (response.ok) {
          const data = await response.json();
          if (mountedRef.current) setItems(data);
        }
      } catch (err) {
        console.error('Failed to fetch shop items:', err);
      }
    };
    const fetchEggOfferings = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/shop/eggs`);
        if (response.ok) {
          const data = await response.json();
          if (mountedRef.current) setEggOfferings(data.offerings || []);
        }
      } catch (err) {
        console.error('Failed to fetch egg offerings:', err);
      }
    };
    fetchShopItems();
    fetchEggOfferings();
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
          if (mountedRef.current) setBalance(data);
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
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/inventory/purchase`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${sessionToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ item_id: itemId, quantity: 1 }),
      });
      if (response.ok) {
        const item = items.find(i => i.item_id === itemId);
        setMessage(`Purchased ${item?.name}!`);
        const balanceRes = await fetch(`${import.meta.env.VITE_API_URL}/api/economy/balance`, {
          headers: { Authorization: `Bearer ${sessionToken}` },
        });
        if (balanceRes.ok) {
          const balanceData = await balanceRes.json();
          if (mountedRef.current) setBalance(balanceData);
        }
      } else {
        const err = await response.json();
        setMessage(err.detail || 'Purchase failed');
      }
    } catch (err) {
      setMessage('Network error');
    } finally {
      if (mountedRef.current) setPurchasing(null);
    }
  };

  const handleEggPurchase = async (rarity: string) => {
    if (!sessionToken) return;
    setPurchasing(rarity);
    setMessage(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/shop/eggs/purchase`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${sessionToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ rarity }),
      });
      if (response.ok) {
        const result = await response.json();
        const upgradeText = result.upgraded ? ` (Upgraded to ${result.rarity}!)` : '';
        setMessage(`Purchased ${result.rarity} egg${upgradeText}`);
        const balanceRes = await fetch(`${import.meta.env.VITE_API_URL}/api/economy/balance`, {
          headers: { Authorization: `Bearer ${sessionToken}` },
        });
        if (balanceRes.ok) {
          const balanceData = await balanceRes.json();
          if (mountedRef.current) setBalance(balanceData);
        }
      } else {
        const err = await response.json();
        setMessage(err.detail || 'Purchase failed');
      }
    } catch (err) {
      setMessage('Network error');
    } finally {
      if (mountedRef.current) setPurchasing(null);
    }
  };

  return (
    <div className="economy-view">
      <div className="economy-header">
        <h1>Trading Post</h1>
        <div className="economy-balance">
          <img className="balance-icon" src="/assets/Currency & Resource/ELE_Dust_20.png" alt="" />
          <span className="balance-amount">{dust.toLocaleString()}</span>
          <span className="balance-separator">|</span>
          <img className="balance-icon" src="/assets/Currency & Resource/ELE_Shard_20.png" alt="" />
          <span className="balance-amount">{shard.toLocaleString()}</span>
        </div>
      </div>
      
      <div className="economy-tabs">
        <button className={`economy-tab ${tab === 'shop' ? 'active' : ''}`} onClick={() => setTab('shop')}>Shop</button>
        <button className={`economy-tab ${tab === 'eggs' ? 'active' : ''}`} onClick={() => setTab('eggs')}>Eggs</button>
        <button className={`economy-tab ${tab === 'history' ? 'active' : ''}`} onClick={() => setTab('history')}>History</button>
      </div>

      {message && <div className="game-message">{message}</div>}

      {tab === 'shop' && (
        <div className="shop-grid">
          {items.map((item) => (
            <div key={item.item_id} className="shop-card">
              <div className="shop-card-icon">
                <img className="item-image" src={ITEM_ICONS[item.item_id] || '/assets/Hatch System/Egg_Common.png'} alt={item.name} />
              </div>
              <div className="shop-card-info">
                <span className="item-name">{item.name}</span>
                <span className="item-description">{item.description}</span>
              </div>
              <div className="shop-card-purchase">
                <span className="item-cost">✦ {item.cost}</span>
                <button
                  className="btn-buy"
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

      {tab === 'eggs' && (
        <div className="shop-grid">
          {eggOfferings.map((egg) => (
            <div key={egg.rarity} className="shop-card">
              <div className="shop-card-icon">
                <img className="item-image" src={EGG_IMAGES[egg.rarity] || EGG_IMAGES.common} alt={egg.rarity} />
              </div>
              <div className="shop-card-info">
                <span className="item-name" style={{ color: RARITY_COLORS[egg.rarity] }}>{egg.rarity}</span>
                <span className="item-description">
                  Random {egg.rarity} companion
                  {egg.upgrade_chance > 0 && ` (${Math.round(egg.upgrade_chance * 100)}% chance for next tier)`}
                </span>
              </div>
              <div className="shop-card-purchase">
                <span className="item-cost">◆ {egg.cost}</span>
                <button
                  className="btn-buy"
                  onClick={() => handleEggPurchase(egg.rarity)}
                  disabled={shard < egg.cost || purchasing === egg.rarity}
                >
                  {purchasing === egg.rarity ? '...' : 'Buy'}
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
          <span className={`tx-type ${tx.type}`}>{tx.type === 'award' ? '+' : '-'}{tx.amount}</span>
          <span className="tx-currency">{tx.currency}</span>
          <span className="tx-source">{tx.source || tx.sink}</span>
        </div>
      ))}
    </div>
  );
}
