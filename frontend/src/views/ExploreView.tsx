import { useState, useEffect, useRef } from 'react';
import { useAuthStore } from '../stores/authStore';

interface Biome {
  zone_id: string;
  name: string;
  description: string;
  resources: string[];
  risk_level: number;
  in_phase1: boolean;
}

interface Expedition {
  uuid: string;
  biome_zone: string;
  dispatched_at: string;
  returns_at: string;
  status: string;
  risk_level: number;
}

const BIOMES: Biome[] = [
  { zone_id: 'verdant_hollow', name: 'Verdant Hollow', description: 'A lush forest clearing with gentle creatures', resources: ['Basic food', 'Common materials', 'Dust'], risk_level: 0.125, in_phase1: true },
  { zone_id: 'mirelands', name: 'Mirelands', description: 'Decay and renewal in the swamp', resources: ['Rare herbs', 'Mutagenic compounds'], risk_level: 0.3, in_phase1: false },
  { zone_id: 'stonecrest', name: 'Stonecrest', description: 'Endurance and perspective in the mountains', resources: ['Minerals', 'Shard precursors'], risk_level: 0.5, in_phase1: false },
  { zone_id: 'emberfall', name: 'Emberfall', description: 'Transformation and danger in the volcanic zone', resources: ['Rare minerals', 'Cuboid shards'], risk_level: 0.7, in_phase1: false },
  { zone_id: 'tek_ruins', name: 'Tek-Ruins', description: 'Memory and the Oracle in ancient ruins', resources: ['Oracle fragments', 'Data crystals'], risk_level: 0.8, in_phase1: false },
  { zone_id: 'threshold', name: 'The Threshold', description: 'The space between worlds', resources: ['Legacy fragments', 'Rescue signals'], risk_level: 0.9, in_phase1: false },
];

const DURATION_OPTIONS = [
  { value: '30m', label: '30 minutes' },
  { value: '2h', label: '2 hours' },
  { value: '8h', label: '8 hours' },
];

export function ExploreView() {
  const [biomes] = useState<Biome[]>(BIOMES);
  const [selectedBiome, setSelectedBiome] = useState<string | null>(null);
  const [duration, setDuration] = useState<string>('2h');
  const [dispatchMsg, setDispatchMsg] = useState<string | null>(null);
  const [expeditions, setExpeditions] = useState<Expedition[]>([]);
  const [loading, setLoading] = useState(false);
  const sessionToken = useAuthStore((s) => s.sessionToken);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const fetchExpeditions = async () => {
    if (!sessionToken) return;
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/expeditions/active`, {
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!response.ok) return;
      const data = await response.json();
      if (mountedRef.current) {
        setExpeditions(data);
      }
    } catch (err) {
      console.error('Failed to fetch expeditions:', err);
    }
  };

  useEffect(() => {
    fetchExpeditions();
  }, [sessionToken]);

  const handleDispatch = async () => {
    if (!sessionToken || !selectedBiome || loading) return;
    
    if (mountedRef.current) setLoading(true);
    if (mountedRef.current) setDispatchMsg(null);
    
    try {
      // Get first available companion
      const companionsResp = await fetch(`${import.meta.env.VITE_API_URL}/api/companions`, {
        headers: { Authorization: `Bearer ${sessionToken}` },
      });
      if (!companionsResp.ok) {
        if (mountedRef.current) setDispatchMsg('Failed to fetch companions');
        if (mountedRef.current) setLoading(false);
        return;
      }
      const companions = await companionsResp.json();
      if (!companions || companions.length === 0) {
        if (mountedRef.current) setDispatchMsg('No companions available');
        if (mountedRef.current) setLoading(false);
        return;
      }
      
      const companionUuid = companions[0].uuid;
      
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/expeditions/dispatch`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${sessionToken}` },
        body: JSON.stringify({ companion_uuid: companionUuid, biome_zone: selectedBiome, duration_hours: duration }),
      });
      
      if (!mountedRef.current) return;
      
      if (response.ok) {
        if (mountedRef.current) setDispatchMsg('Expedition dispatched!');
        await fetchExpeditions();
      } else {
        try {
          const err = await response.json();
          if (mountedRef.current) setDispatchMsg(err.detail || 'Dispatch failed');
        } catch {
          if (mountedRef.current) setDispatchMsg('Dispatch failed');
        }
      }
    } catch (err) {
      console.error('Dispatch error:', err);
      if (mountedRef.current) setDispatchMsg('Network error');
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  };

  const selected = BIOMES.find(b => b.zone_id === selectedBiome);

  return (
    <div className="explore-view">
      <h1>Explore</h1>

      {dispatchMsg && <div className="game-message">{dispatchMsg}</div>}

      <div className="biome-grid">
        {biomes.map(biome => (
          <div
            key={biome.zone_id}
            className={`biome-card ${!biome.in_phase1 ? 'locked' : ''} ${selectedBiome === biome.zone_id ? 'selected' : ''}`}
            onClick={() => biome.in_phase1 && setSelectedBiome(biome.zone_id)}
          >
            <div className="biome-info">
              <h3>{biome.name}</h3>
              <p>{biome.description}</p>
              <div className="biome-resources">
                {biome.resources.map(r => <span key={r} className="resource-tag">{r}</span>)}
              </div>
              <div className="risk-meter">
                <span>Risk:</span>
                <div className="meter small">
                  <div className="meter-fill risk" style={{ width: `${biome.risk_level * 100}%` }} />
                </div>
              </div>
            </div>
            {!biome.in_phase1 && <div className="lock-overlay">🔒</div>}
          </div>
        ))}
      </div>

      {selected && (
        <div className="dispatch-panel">
          <h3>Dispatch to {selected.name}</h3>
          <div className="duration-select">
            {DURATION_OPTIONS.map(d => (
              <button
                key={d.value}
                className={`duration-btn ${duration === d.value ? 'active' : ''}`}
                onClick={() => setDuration(d.value)}
              >
                {d.label}
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
              <span>{exp.biome_zone}</span>
              <span>{exp.status}</span>
              <span>{new Date(exp.returns_at).toLocaleTimeString()}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
