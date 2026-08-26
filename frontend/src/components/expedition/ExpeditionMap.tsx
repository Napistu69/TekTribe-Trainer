import { useExpeditionStore } from '../../stores/expeditionStore';

interface Biome {
  zone_id: string;
  name: string;
  description: string;
  risk_level: number;
  in_phase1: boolean;
}

const BIOMES: Biome[] = [
  { zone_id: 'verdant_hollow', name: 'Verdant Hollow', description: 'A lush forest clearing. Perfect for new companions.', risk_level: 0.125, in_phase1: true },
  { zone_id: 'mirelands', name: 'Mirelands', description: 'A swampy wetland teeming with rare herbs.', risk_level: 0.3, in_phase1: false },
  { zone_id: 'stonecrest', name: 'Stonecrest', description: 'Mountain peaks offering rare minerals.', risk_level: 0.4, in_phase1: false },
  { zone_id: 'emberfall', name: 'Emberfall', description: 'Volcanic terrain with rare minerals.', risk_level: 0.55, in_phase1: false },
  { zone_id: 'tek_ruins', name: 'Tek-Ruins', description: 'Ancient ruins filled with Oracle fragments.', risk_level: 0.5, in_phase1: false },
  { zone_id: 'void_center', name: 'Void Center', description: 'A liminal space between worlds.', risk_level: 0.65, in_phase1: false },
];

interface ExpeditionMapProps {
  onSelectBiome: (biomeId: string) => void;
}

export function ExpeditionMap({ onSelectBiome }: ExpeditionMapProps) {
  const selectedBiome = useExpeditionStore((s) => s.selectedBiome);
  
  return (
    <div className="expedition-map">
      <h2>Explore</h2>
      <p className="subtitle">Choose a biome to explore</p>
      
      <div className="biomes-grid">
        {BIOMES.map((biome) => (
          <button
            key={biome.zone_id}
            className={`biome-card ${selectedBiome === biome.zone_id ? 'selected' : ''} ${!biome.in_phase1 ? 'locked' : ''}`}
            onClick={() => biome.in_phase1 && onSelectBiome(biome.zone_id)}
            disabled={!biome.in_phase1}
          >
            <div className="biome-header">
              <span className="biome-name">{biome.name}</span>
              {!biome.in_phase1 && <span className="lock-icon">🔒</span>}
            </div>
            <p className="biome-description">{biome.description}</p>
            <div className="biome-risk">
              <span className="risk-label">Risk:</span>
              <span className={`risk-value ${biome.risk_level <= 0.2 ? 'low' : biome.risk_level <= 0.4 ? 'medium' : 'high'}`}>
                {Math.round(biome.risk_level * 100)}%
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
