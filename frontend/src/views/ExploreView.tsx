import { useState, useEffect, useRef } from 'react';
import { useAuthStore } from '../stores/authStore';
import { TutorialOverlay, useTutorial } from '../components/shared/TutorialOverlay';

const TUTORIAL_STEPS = [
  { title: 'Exploration', text: 'Dispatch your companions on expeditions to explore biomes and gather resources.' },
  { title: 'Biomes', text: 'Each biome has different resources and risk levels. Start with Verdant Hollow for safer expeditions.' },
  { title: 'Countdown & Collect', text: 'Expeditions take time. When they return, click Collect to gather your rewards.' },
];

interface Expedition {
  uuid: string;
  companion_uuid: string;
  biome_zone: string;
  dispatched_at: string;
  returns_at: string;
  status: string;
  risk_level: number;
  result?: {
    success: boolean;
    dust_gained: number;
    companion_injured: boolean;
    oracle_fragment_found: boolean;
    encounter_story: string;
    imprint_change: number;
    resources_gained: string[];
  };
}

interface Companion {
  uuid: string;
  species: string;
  current_state: string;
}

interface Biome {
  zone_id: string;
  name: string;
  description: string;
  resources: string[];
  risk_level: number;
  in_phase1: boolean;
  imagePrefix: string;
}

const BIOMES: Biome[] = [
  { zone_id: 'verdant_hollow', name: 'Verdant Hollow', description: 'A lush forest clearing with gentle creatures', resources: ['Basic food', 'Common materials', 'Dust'], risk_level: 0.125, in_phase1: true, imagePrefix: 'Verdant_Hollow' },
  { zone_id: 'mirelands', name: 'Mirelands', description: 'Decay and renewal in the swamp', resources: ['Rare herbs', 'Mutagenic compounds'], risk_level: 0.3, in_phase1: false, imagePrefix: 'Mirelands' },
  { zone_id: 'stonecrest', name: 'Stonecrest', description: 'Endurance and perspective in the mountains', resources: ['Minerals', 'Shard precursors'], risk_level: 0.5, in_phase1: false, imagePrefix: 'Stonecrest' },
  { zone_id: 'emberfall', name: 'Emberfall', description: 'Transformation and danger in the volcanic zone', resources: ['Rare minerals', 'Cuboid shards'], risk_level: 0.7, in_phase1: false, imagePrefix: 'Emberfall' },
  { zone_id: 'tek_ruins', name: 'Tek-Ruins', description: 'Memory and the Oracle in ancient ruins', resources: ['Oracle fragments', 'Data crystals'], risk_level: 0.8, in_phase1: false, imagePrefix: 'Tek_Ruins' },
  { zone_id: 'void_center', name: 'Void Center', description: 'The space between worlds', resources: ['Legacy fragments', 'Rescue signals'], risk_level: 0.9, in_phase1: false, imagePrefix: 'Void_Center' },
];

export function ExploreView() {
  const [selectedBiome, setSelectedBiome] = useState<string | null>(null);
  const [duration, setDuration] = useState('2h');
  const [dispatchMsg, setDispatchMsg] = useState<string | null>(null);
  const [expeditions, setExpeditions] = useState<Expedition[]>([]);
  const [history, setHistory] = useState<Expedition[]>([]);
  const [companions, setCompanions] = useState<Companion[]>([]);
  const [loading, setLoading] = useState(false);
  const [now, setNow] = useState(Date.now());
  const { showTutorial, completeTutorial } = useTutorial('tutorial-explore');
  const sessionToken = useAuthStore((s) => s.sessionToken);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);

  const fetchExpeditions = async () => {
    if (!sessionToken) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/expeditions/active`, {
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!response.ok) return;
      const data = await response.json();
      if (mountedRef.current) setExpeditions(data);
    } catch (err) {
      console.error('Failed to fetch expeditions:', err);
    }
  };

  const fetchHistory = async () => {
    if (!sessionToken) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/expeditions/history`, {
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!response.ok) return;
      const data = await response.json();
      if (mountedRef.current) setHistory(data);
    } catch (err) {
      console.error('Failed to fetch history:', err);
    }
  };

  const fetchCompanions = async () => {
    if (!sessionToken) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/companions`, {
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!response.ok) return;
      const data = await response.json();
      if (mountedRef.current) setCompanions(data);
    } catch (err) {
      console.error('Failed to fetch companions:', err);
    }
  };

  useEffect(() => {
    fetchExpeditions();
    fetchHistory();
    fetchCompanions();
  }, [sessionToken]);

  const handleDispatch = async () => {
    if (!sessionToken || !selectedBiome || loading) return;
    setLoading(true);
    setDispatchMsg(null);
    try {
      const availableCompanions = companions.filter(c => c.current_state !== 'on_expedition');
      if (availableCompanions.length === 0) {
        setDispatchMsg('No companions available (all on expedition)');
        setLoading(false);
        return;
      }
      const companionUuid = availableCompanions[0].uuid;
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/expeditions/dispatch`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${sessionToken}` },
        body: JSON.stringify({ companion_uuid: companionUuid, biome_zone: selectedBiome, duration_hours: duration }),
      });
      if (!mountedRef.current) return;
      if (response.ok) {
        setDispatchMsg('Expedition dispatched!');
        await fetchExpeditions();
        await fetchCompanions();
      } else {
        try {
          const err = await response.json();
          setDispatchMsg(err.detail || 'Dispatch failed');
        } catch {
          setDispatchMsg('Dispatch failed');
        }
      }
    } catch (err) {
      console.error('Dispatch error:', err);
      if (mountedRef.current) setDispatchMsg('Network error');
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  };

  const handleCollect = async (expeditionUuid: string) => {
    if (!sessionToken) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/expeditions/${expeditionUuid}/collect`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!mountedRef.current) return;
      if (response.ok) {
        await fetchExpeditions();
        await fetchHistory();
        await fetchCompanions();
      } else {
        try { const err = await response.json(); setDispatchMsg(err.detail || 'Collect failed'); } catch { setDispatchMsg('Collect failed'); }
      }
    } catch (err) {
      if (mountedRef.current) setDispatchMsg('Network error');
    }
  };

  const handleCancel = async (expeditionUuid: string) => {
    if (!sessionToken) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/expeditions/${expeditionUuid}/cancel`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!mountedRef.current) return;
      if (response.ok) {
        setDispatchMsg('Expedition cancelled — companion returned!');
        await fetchExpeditions();
        await fetchCompanions();
      } else {
        try { const err = await response.json(); setDispatchMsg(err.detail || 'Cancel failed'); } catch { setDispatchMsg('Cancel failed'); }
      }
    } catch (err) {
      if (mountedRef.current) setDispatchMsg('Network error');
    }
  };

  const getCountdown = (returnsAt: string) => {
    const diff = new Date(returnsAt).getTime() - now;
    if (diff <= 0) return 'Ready!';
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    return `${hours}h ${minutes}m ${seconds}s`;
  };

  const isReady = (returnsAt: string) => new Date(returnsAt).getTime() <= now;

  const selected = BIOMES.find(b => b.zone_id === selectedBiome);

  return (
    <div className="explore-view">
      {showTutorial && <TutorialOverlay steps={TUTORIAL_STEPS} storageKey="tutorial-explore" onComplete={completeTutorial} />}
      <h1>Explore</h1>
      {dispatchMsg && <div className="game-message">{dispatchMsg}</div>}
      <div className="biome-grid">
        {BIOMES.map(biome => (
          <div
            key={biome.zone_id}
            className={`biome-card ${!biome.in_phase1 ? 'locked' : ''} ${selectedBiome === biome.zone_id ? 'selected' : ''}`}
            onClick={() => biome.in_phase1 && setSelectedBiome(biome.zone_id)}
          >
            <div className="biome-image-container">
              <picture>
                <source
                  type="image/avif"
                  srcSet={`/assets/Explore & Biomes/${biome.imagePrefix}_Square.avif`}
                />
                <img
                  src={`/assets/Explore & Biomes/${biome.imagePrefix}_Square.png`}
                  alt={biome.name}
                  className="biome-card-image"
                  loading="lazy"
                  decoding="async"
                />
              </picture>
            </div>
            <div className="biome-info">
              <h3>{biome.name}</h3>
              <p>{biome.description}</p>
              <div className="biome-resources">{biome.resources.map(r => <span key={r} className="resource-tag">{r}</span>)}</div>
              <div className="risk-meter"><span>Risk:</span><div className="meter small"><div className="meter-fill risk" style={{ width: `${biome.risk_level * 100}%` }} /></div></div>
            </div>
            {!biome.in_phase1 && <div className="lock-overlay">🔒</div>}
          </div>
        ))}
      </div>
      {selected && (
        <div className="dispatch-panel">
          <div className="dispatch-hero">
            <picture>
              <source
                type="image/avif"
                srcSet={`/assets/Explore & Biomes/${selected.imagePrefix}_Landscape.avif`}
              />
              <img
                src={`/assets/Explore & Biomes/${selected.imagePrefix}_Landscape.png`}
                alt={selected.name}
                className="dispatch-hero-image"
                loading="eager"
                decoding="async"
              />
            </picture>
          </div>
          <h3>Dispatch to {selected.name}</h3>
          <div className="duration-select">
            {['2h', '6h', '12h', '24h'].map(d => (
              <button key={d} className={`duration-btn ${duration === d ? 'active' : ''}`} onClick={() => setDuration(d)}>
                {d === '2h' ? '2 hours' : d === '6h' ? '6 hours' : d === '12h' ? '12 hours' : '24 hours'}
              </button>
            ))}
          </div>
          <button className="btn-primary dispatch-btn" onClick={handleDispatch} disabled={loading}>
            {loading ? 'Dispatching...' : 'Dispatch Expedition'}
          </button>
        </div>
      )}
      {expeditions.length > 0 && (
        <div className="expeditions-panel">
          <h3>Active Expeditions</h3>
          {expeditions.map(exp => (
            <div key={exp.uuid} className="expedition-row">
              <div className="expedition-info">
                <span className="expedition-biome">{exp.biome_zone}</span>
                <span className="expedition-countdown">{getCountdown(exp.returns_at)}</span>
              </div>
              {isReady(exp.returns_at) ? (
                <div className="expedition-actions">
                  <button className="btn-primary collect-btn" onClick={() => handleCollect(exp.uuid)}>Collect</button>
                  <button className="btn-secondary cancel-btn" onClick={() => handleCancel(exp.uuid)}>Cancel</button>
                </div>
              ) : (
                <button className="btn-secondary cancel-btn" onClick={() => handleCancel(exp.uuid)}>Cancel</button>
              )}
            </div>
          ))}
        </div>
      )}
      {history.length > 0 && (
        <div className="history-panel">
          <h3>Expedition History</h3>
          {history.slice(0, 5).map(exp => (
            <div key={exp.uuid} className="history-row">
              <span>{exp.biome_zone}</span>
              <span>{exp.result?.success ? 'Success' : 'Failed'}</span>
              <span>+{exp.result?.dust_gained || 0} dust</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
