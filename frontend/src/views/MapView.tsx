import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface Station {
  id: string;
  name: string;
  description: string;
  icon: string;
  image: string;
  route?: string;
  locked: boolean;
  unlockHint?: string;
}

const STATIONS: Station[] = [
  {
    id: 'hatchery',
    name: 'Hatchery',
    description: 'Incubate eggs and hatch new companions',
    icon: '🥚',
    image: '/assets/Habitat & Camp/hatchery.png',
    route: '/hatchery',
    locked: false,
  },
  {
    id: 'nursery',
    name: 'Nursery',
    description: 'Care for hatchlings and juveniles',
    icon: '🐣',
    image: '/assets/Habitat & Camp/nursery.png',
    route: '/camp',
    locked: false,
  },
  {
    id: 'forge',
    name: 'Forge',
    description: 'Refine Dust into Shards and Cuboids',
    icon: '🔥',
    image: '/assets/Habitat & Camp/forge.png',
    locked: true,
    unlockHint: 'Complete 5 hatches to unlock',
  },
  {
    id: 'training_grounds',
    name: 'Training Grounds',
    description: 'Train your companion in mini-games',
    icon: '⚔️',
    image: '/assets/Habitat & Camp/habitat.png',
    route: '/training',
    locked: false,
  },
  {
    id: 'expedition_gate',
    name: 'Expedition Gate',
    description: 'Dispatch companions to explore biomes',
    icon: '🌍',
    image: '/assets/Habitat & Camp/expedition_gate.png',
    route: '/explore',
    locked: false,
  },
  {
    id: 'mining_pit',
    name: 'Mining Pit',
    description: 'Mine Dust with your pickaxe',
    icon: '⛏️',
    image: '/assets/Habitat & Camp/mining_pit.png',
    locked: true,
    unlockHint: 'Hatch your first companion to unlock',
  },
  {
    id: 'overseer_shrine',
    name: 'Overseer Shrine',
    description: 'Commune with the Oracle',
    icon: '👁️',
    image: '/assets/Habitat & Camp/overseer_shrine.png',
    locked: true,
    unlockHint: 'Reach 500 bond with any companion',
  },
];

export function MapView() {
  const navigate = useNavigate();
  const [hoveredStation, setHoveredStation] = useState<string | null>(null);

  const handleStationClick = (station: Station) => {
    if (station.locked || !station.route) return;
    navigate(station.route);
  };

  return (
    <div className="map-view">
      <div className="map-header">
        <h1>TekTribe Trainer</h1>
        <p className="map-subtitle">Select a station to begin</p>
      </div>

      <div className="map-grid">
        {STATIONS.map((station) => (
          <div
            key={station.id}
            className={`station-card ${station.locked ? 'locked' : ''} ${hoveredStation === station.id ? 'hovered' : ''}`}
            onClick={() => handleStationClick(station)}
            onMouseEnter={() => setHoveredStation(station.id)}
            onMouseLeave={() => setHoveredStation(null)}
          >
            <div className="station-image-container">
              <img
                src={station.image}
                alt={station.name}
                className="station-image"
              />
              {station.locked && <div className="station-lock-overlay">🔒</div>}
            </div>
            <div className="station-info">
              <span className="station-icon">{station.icon}</span>
              <h3>{station.name}</h3>
              <p>{station.description}</p>
              {station.locked && station.unlockHint && (
                <span className="unlock-hint">{station.unlockHint}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
