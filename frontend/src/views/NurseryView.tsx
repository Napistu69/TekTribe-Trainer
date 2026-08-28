import { useState, useEffect, useRef } from 'react';
import { useAuthStore } from '../stores/authStore';
import { TutorialOverlay, useTutorial } from '../components/shared/TutorialOverlay';
import { useNavigate } from 'react-router-dom';

const TUTORIAL_STEPS = [
  { title: 'Welcome to the Nursery', text: 'This is where hatchlings and juveniles are cared for. Feed, clean, imprint, and rest your young companions.' },
  { title: 'Care Actions', text: 'Use items from your inventory to care for companions. Imprint and Rest are always free.' },
  { title: 'Growth', text: 'As your companion grows, they will eventually become adults and move to the Camp!' },
];

const COMPANION_IMAGES: Record<string, string> = {
  parasaur: '/assets/Creatures/parasaur_character.png',
  dilo: '/assets/Creatures/dilo_character.png',
  trike: '/assets/Creatures/trike_character.png',
  ptera: '/assets/Creatures/ptera_character.png',
  raptor: '/assets/Creatures/raptor_character.png',
  rex: '/assets/Creatures/rex_character.png',
};

const RARITY_COLORS: Record<string, string> = {
  common: '#808080',
  uncommon: '#00ff00',
  rare: '#00d4ff',
  epic: '#ff00ff',
  ascendant: '#4a9b8f',
  legendary: '#d4a84b',
  mythic: '#ff4444',
};

const DIET_COLORS: Record<string, string> = {
  carnivore: '#ff4444',
  herbivore: '#00c853',
  omnivore: '#2196f3',
  aquatic: '#00bcd4',
};

interface Companion {
  uuid: string;
  species: string;
  name: string;
  life_stage: string;
  rarity: string;
  diet: string;
  imprint_level: number;
  is_locked: boolean;
  current_state: string;
  biological_sex: string;
  maturation_progress: number;
  base_stats: Record<string, number>;
  mutated_stats: Record<string, number>;
  care_state: {
    hunger: number;
    energy: number;
    morale: number;
    cleanliness: number;
  };
}

interface InventoryItem {
  item_id: string;
  name: string;
  description: string;
  quantity: number;
}

const SHARD_AMOUNTS: Record<string, number> = {
  common: 10,
  uncommon: 20,
  rare: 40,
  epic: 75,
  ascendant: 150,
  legendary: 300,
  mythic: 500,
};

function getShardAmount(rarity: string): number {
  return SHARD_AMOUNTS[rarity] || 10;
}

export function NurseryView() {
  const [companion, setCompanion] = useState<Companion | null>(null);
  const [selectedCompanion, setSelectedCompanion] = useState<string | null>(null);
  const [companions, setCompanions] = useState<Companion[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [showFeedMenu, setShowFeedMenu] = useState(false);
  const { showTutorial, completeTutorial } = useTutorial('tutorial-nursery');
  const sessionToken = useAuthStore((s) => s.sessionToken);
  const mountedRef = useRef(true);
  const navigate = useNavigate();

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => {
        if (mountedRef.current) setMessage(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  const isJuvenileOrHatchling = (c: Companion) => c.life_stage === 'hatchling' || c.life_stage === 'juvenile';

  const fetchCompanions = async () => {
    if (!sessionToken) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/companions`, {
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!response.ok) return;
      const data = await response.json();
      if (!mountedRef.current) return;
      const filtered = data.filter(isJuvenileOrHatchling);
      setCompanions(filtered);
      if (filtered.length > 0 && !selectedCompanion) {
        setSelectedCompanion(filtered[0].uuid);
        setCompanion(filtered[0]);
      }
    } catch (err) {
      console.error('Failed to fetch companions:', err);
    }
  };

  const fetchInventory = async () => {
    if (!sessionToken) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/inventory`, {
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!response.ok) return;
      const data = await response.json();
      if (mountedRef.current) setInventory(data.items || []);
    } catch (err) {
      console.error('Failed to fetch inventory:', err);
    }
  };

  useEffect(() => { fetchCompanions(); fetchInventory(); }, [sessionToken]);

  useEffect(() => {
    if (selectedCompanion) {
      const c = companions.find(c => c.uuid === selectedCompanion);
      if (c) setCompanion(c);
    }
  }, [selectedCompanion, companions]);

  const getCompatibleFeeds = (): InventoryItem[] => {
    if (!companion) return [];
    const diet = companion.diet || 'omnivore';
    const feedIds: Record<string, string[]> = {
      carnivore: ['meat', 'jerky'],
      herbivore: ['berries', 'crops'],
      omnivore: ['meat', 'jerky', 'berries', 'crops'],
      aquatic: [],
    };
    const ids = feedIds[diet] || [];
    return inventory.filter(item => ids.includes(item.item_id) && item.quantity > 0);
  };

  const getSponges = (): InventoryItem[] => {
    return inventory.filter(item => item.item_id === 'sponge' && item.quantity > 0);
  };

  const handleUseItem = async (itemId: string) => {
    if (!sessionToken || !selectedCompanion || loading) return;
    setLoading(true);
    setMessage(null);
    setShowFeedMenu(false);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/inventory/use`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${sessionToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ companion_uuid: selectedCompanion, item_id: itemId }),
      });
      if (!mountedRef.current) return;
      if (response.ok) {
        const data = await response.json();
        setMessage(`+${data.dust_gained || 0} dust`);
        if (companion && data.care_state) {
          setCompanion({ ...companion, care_state: data.care_state, imprint_level: data.imprint_level ?? companion.imprint_level });
        }
        await fetchInventory();
      } else {
        const err = await response.json();
        setMessage(err.detail || 'Action failed');
      }
    } catch (err) {
      if (mountedRef.current) setMessage('Network error');
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  };

  const handleFreeAction = async (action: string) => {
    if (!sessionToken || !selectedCompanion || loading) return;
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/inventory/free-action`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${sessionToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ companion_uuid: selectedCompanion, action }),
      });
      if (!mountedRef.current) return;
      if (response.ok) {
        const data = await response.json();
        setMessage(`+${data.dust_gained || 0} dust`);
        if (companion && data.care_state) {
          setCompanion({ ...companion, care_state: data.care_state, imprint_level: data.imprint_level ?? companion.imprint_level });
        }
      } else {
        const err = await response.json();
        setMessage(err.detail || 'Action failed');
      }
    } catch (err) {
      if (mountedRef.current) setMessage('Network error');
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  };

  const handleRelease = async (companionUuid: string) => {
    if (!sessionToken) return;
    if (!confirm('Are you sure you want to release this companion? This cannot be undone.')) return;
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/companions/${companionUuid}/release`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!mountedRef.current) return;
      if (response.ok) {
        try {
          const result = await response.json();
          setMessage(`Released! +${result.shards_gained} shards`);
        } catch {
          setMessage('Released!');
        }
        const updatedResponse = await fetch(`${import.meta.env.VITE_API_URL}/api/companions`, {
          headers: { Authorization: `Bearer ${sessionToken}` },
        });
        if (updatedResponse.ok && mountedRef.current) {
          const data = await updatedResponse.json();
          const filtered = data.filter(isJuvenileOrHatchling);
          setCompanions(filtered);
          if (filtered.length > 0) {
            setSelectedCompanion(filtered[0].uuid);
            setCompanion(filtered[0]);
          } else {
            setSelectedCompanion(null);
            setCompanion(null);
          }
        }
      } else {
        try { const err = await response.json(); setMessage(err.detail || 'Release failed'); } catch { setMessage('Release failed'); }
      }
    } catch (err) {
      if (mountedRef.current) setMessage('Network error');
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  };

  const handleToggleLock = async (companionUuid: string) => {
    if (!sessionToken) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/companions/${companionUuid}/lock`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!mountedRef.current) return;
      if (response.ok) {
        const result = await response.json();
        if (companion && companion.uuid === companionUuid) {
          setCompanion({ ...companion, is_locked: result.is_locked });
        }
        await fetchCompanions();
      }
    } catch (err) {
      console.error('Lock toggle error:', err);
    }
  };

  if (!companion) {
    return (
      <div className="nursery-view">
        {showTutorial && <TutorialOverlay steps={TUTORIAL_STEPS} storageKey="tutorial-nursery" onComplete={completeTutorial} />}
        <h1>Nursery</h1>
        <div className="empty-nursery">
          <p>No hatchlings or juveniles yet. Hatch an egg to get started!</p>
        </div>
      </div>
    );
  }

  const compatibleFeeds = getCompatibleFeeds();
  const sponges = getSponges();

  return (
    <div className="nursery-view">
      {showTutorial && <TutorialOverlay steps={TUTORIAL_STEPS} storageKey="tutorial-nursery" onComplete={completeTutorial} />}
      <h1>Nursery</h1>
      {message && <div className="game-message">{message}</div>}
      <div className="companion-selector">
        {companions.map(c => (
          <button key={c.uuid} className={`companion-tab ${selectedCompanion === c.uuid ? 'active' : ''}`} onClick={() => setSelectedCompanion(c.uuid)}>
            {c.species.charAt(0).toUpperCase() + c.species.slice(1)}
          </button>
        ))}
      </div>
      <div className="companion-display">
        <div className="companion-visual">
          <img src={COMPANION_IMAGES[companion.species] || COMPANION_IMAGES.raptor} alt={companion.species} className="companion-image" />
          <div className="companion-info">
            <div className="companion-name-row">
              <h2>{companion.name || companion.species.charAt(0).toUpperCase() + companion.species.slice(1)}</h2>
              <button className="btn-rename" onClick={() => {
                const newName = prompt('Enter a name for your companion:', companion.name || companion.species);
                if (newName && newName.trim()) {
                  fetch(`${import.meta.env.VITE_API_URL}/api/companions/${companion.uuid}/name`, {
                    method: 'PATCH',
                    headers: { Authorization: `Bearer ${sessionToken}`, 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: newName.trim() }),
                  }).then(r => r.json()).then(() => {
                    if (mountedRef.current) {
                      setCompanion({ ...companion, name: newName.trim() });
                    }
                  });
                }
              }}>✏️</button>
            </div>
            <span className="life-stage">{companion.life_stage.charAt(0).toUpperCase() + companion.life_stage.slice(1)}</span>
            <span className="diet-tag" style={{ color: DIET_COLORS[companion.diet] || '#2196f3' }}>{companion.diet ? companion.diet.charAt(0).toUpperCase() + companion.diet.slice(1) : 'Unknown'}</span>
            <span className="sex-tag">{companion.biological_sex === 'male' ? '♂' : companion.biological_sex === 'female' ? '♀' : '?'}</span>
            <div className="imprint-bar">
              <span>Imprint: {companion.imprint_level}/100</span>
              <div className="meter">
                <div className="meter-fill" style={{ width: `${(companion.imprint_level / 100) * 100}%` }} />
              </div>
            </div>
            <div className="rarity-tag" style={{ color: RARITY_COLORS[companion.rarity] }}>{companion.rarity}</div>
            <div className="maturation-bar">
              <span>Maturation: {Math.round((companion.maturation_progress || 0) * 100)}%</span>
              <div className="meter"><div className="meter-fill" style={{ width: `${(companion.maturation_progress || 0) * 100}%` }} /></div>
            </div>
            {companion.current_state === 'on_expedition' && (
              <span className="expedition-badge">🗺️ On Expedition</span>
            )}
          </div>
        </div>

        <div className="companion-actions">
          <button 
            className={`btn-icon ${companion.is_locked ? 'locked' : ''}`} 
            onClick={() => handleToggleLock(companion.uuid)}
            title={companion.is_locked ? 'Unlock' : 'Lock'}
          >
            {companion.is_locked ? '🔒' : '🔓'}
          </button>
          {!companion.is_locked && (
            <button className="btn-secondary release-btn" onClick={() => handleRelease(companion.uuid)}>
              Release ({getShardAmount(companion.rarity)} shards)
            </button>
          )}
        </div>

        <div className="stats-panel">
          <h3>Stats</h3>
          {Object.entries(companion.mutated_stats).length > 0 ? (
            <div className="stats-grid">
              {Object.entries(companion.mutated_stats).map(([stat, value]) => (
                <div key={stat} className="stat-item">
                  <span className="stat-name">{stat.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</span>
                  <span className="stat-value">{typeof value === 'number' ? value.toFixed(1) : value}</span>
                </div>
              ))}
            </div>
          ) : Object.entries(companion.base_stats).length > 0 ? (
            <div className="stats-grid">
              {Object.entries(companion.base_stats).map(([stat, value]) => (
                <div key={stat} className="stat-item">
                  <span className="stat-name">{stat.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</span>
                  <span className="stat-value">{typeof value === 'number' ? value.toFixed(1) : value}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="no-stats">No stats yet — train your companion!</p>
          )}
        </div>

        <div className="care-meters">
          <div className="care-meter">
            <div className="care-meter-label"><span>Hunger</span><span>{Math.round((companion.care_state?.hunger ?? 0) * 100)}%</span></div>
            <div className="meter"><div className="meter-fill" style={{ width: `${(companion.care_state?.hunger ?? 0) * 100}%`, background: '#ff6b6b' }} /></div>
          </div>
          <div className="care-meter">
            <div className="care-meter-label"><span>Energy</span><span>{Math.round((companion.care_state?.energy ?? 0) * 100)}%</span></div>
            <div className="meter"><div className="meter-fill" style={{ width: `${(companion.care_state?.energy ?? 0) * 100}%`, background: '#ffd93d' }} /></div>
          </div>
          <div className="care-meter">
            <div className="care-meter-label"><span>Morale</span><span>{Math.round((companion.care_state?.morale ?? 0) * 100)}%</span></div>
            <div className="meter"><div className="meter-fill" style={{ width: `${(companion.care_state?.morale ?? 0) * 100}%`, background: '#6bcb77' }} /></div>
          </div>
          <div className="care-meter">
            <div className="care-meter-label"><span>Cleanliness</span><span>{Math.round((companion.care_state?.cleanliness ?? 0) * 100)}%</span></div>
            <div className="meter"><div className="meter-fill" style={{ width: `${(companion.care_state?.cleanliness ?? 0) * 100}%`, background: '#4d96ff' }} /></div>
          </div>
        </div>
        <div className="care-actions">
          <div className="care-action-group">
            <button className="care-action-btn" onClick={() => setShowFeedMenu(!showFeedMenu)} disabled={loading || companion.current_state === 'on_expedition'}>
              <span className="care-icon">🥩</span>
              <span className="care-label">Feed</span>
            </button>
            {showFeedMenu && (
              <div className="feed-menu">
                {compatibleFeeds.length > 0 ? (
                  compatibleFeeds.map(item => (
                    <button key={item.item_id} className="feed-option" onClick={() => handleUseItem(item.item_id)}>
                      {item.name} ×{item.quantity}
                    </button>
                  ))
                ) : (
                  <div className="feed-empty">
                    <p>No feed in inventory</p>
                    <button className="btn-buy-link" onClick={() => navigate('/economy')}>Buy from Shop</button>
                  </div>
                )}
              </div>
            )}
          </div>
          <button className="care-action-btn" onClick={() => handleUseItem('sponge')} disabled={loading || sponges.length === 0 || companion.current_state === 'on_expedition'}>
            <span className="care-icon">🧽</span>
            <span className="care-label">Clean {sponges.length > 0 && `(${sponges[0].quantity})`}</span>
          </button>
          <button className="care-action-btn" onClick={() => handleFreeAction('imprint')} disabled={loading || companion.current_state === 'on_expedition'}>
            <span className="care-icon">💚</span>
            <span className="care-label">Imprint</span>
          </button>
          <button className="care-action-btn" onClick={() => handleFreeAction('rest')} disabled={loading || companion.current_state === 'on_expedition'}>
            <span className="care-icon">💤</span>
            <span className="care-label">Rest</span>
          </button>
        </div>
      </div>
    </div>
  );
}
