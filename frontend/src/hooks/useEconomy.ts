import { useAuthStore } from '../stores/authStore';
import { useEconomyStore } from '../stores/economyStore';

export function useEconomy() {
  const sessionToken = useAuthStore((s) => s.sessionToken);
  const setBalance = useEconomyStore((s) => s.setBalance);
  const setTransactions = useEconomyStore((s) => s.setTransactions);

  const fetchBalance = async () => {
    if (!sessionToken) return;
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

  const fetchHistory = async () => {
    if (!sessionToken) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/economy/history`, {
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (response.ok) {
        const data = await response.json();
        setTransactions(data.transactions);
      }
    } catch (err) {
      console.error('Failed to fetch history:', err);
    }
  };

  const fetchShopItems = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/economy/shop`);
      if (response.ok) {
        return await response.json();
      }
    } catch (err) {
      console.error('Failed to fetch shop items:', err);
    }
    return [];
  };

  const purchaseItem = async (itemId: string, companionUuid: string) => {
    if (!sessionToken) return { success: false, error: 'Not authenticated' };
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/economy/shop/purchase`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${sessionToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ item_id: itemId, companion_uuid: companionUuid }),
      });
      if (response.ok) {
        const data = await response.json();
        await fetchBalance();
        return { success: true, data };
      } else {
        const err = await response.json();
        return { success: false, error: err.detail || 'Purchase failed' };
      }
    } catch (err) {
      console.error('Purchase error:', err);
      return { success: false, error: 'Network error' };
    }
  };

  return { fetchBalance, fetchHistory, fetchShopItems, purchaseItem };
}
