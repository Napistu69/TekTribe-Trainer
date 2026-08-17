import { useState } from 'react';
import { useEconomyStore } from '../../stores/economyStore';

interface ShopItem {
  item_id: string;
  name: string;
  description: string;
  cost: number;
  effect: any;
  category: string;
}

interface ShopViewProps {
  companionUuid: string;
  onPurchase: (itemId: string, companionUuid: string) => void;
}

export function ShopView({ companionUuid, onPurchase }: ShopViewProps) {
  const dust = useEconomyStore((s) => s.dust);
  const [items] = useState<ShopItem[]>([
    { item_id: 'basic_food', name: 'Basic Food', description: 'Restores hunger', cost: 10, effect: {}, category: 'consumable' },
    { item_id: 'medicine', name: 'Medicine', description: 'Heals +30% HP', cost: 50, effect: {}, category: 'consumable' },
    { item_id: 'care_kit', name: 'Care Kit', description: 'Restore all meters to 70%', cost: 30, effect: {}, category: 'consumable' },
    { item_id: 'incubation_boost', name: 'Incubation Boost', description: 'Accelerate incubation by 25%', cost: 100, effect: {}, category: 'consumable' },
  ]);
  const [purchasing, setPurchasing] = useState<string | null>(null);
  
  const handlePurchase = (itemId: string) => {
    setPurchasing(itemId);
    onPurchase(itemId, companionUuid);
    setTimeout(() => setPurchasing(null), 1000);
  };
  
  return (
    <div className="shop-view">
      <div className="shop-header">
        <h2>Shop</h2>
        <div className="shop-balance">
          <span className="dust-icon">✦</span>
          <span>{dust} Dust</span>
        </div>
      </div>
      
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
    </div>
  );
}
