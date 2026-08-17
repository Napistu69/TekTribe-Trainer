import { useState, useEffect } from 'react';
import { CompanionSelector } from '../components/camp/CompanionSelector';
import { CompanionModel } from '../components/camp/CompanionModel';
import { CareMeters } from '../components/camp/CareMeters';
import { CareActions } from '../components/camp/CareActions';
import { StatsPanel } from '../components/camp/StatsPanel';
import { PersonalityCard } from '../components/camp/PersonalityCard';
import { BondProgress } from '../components/camp/BondProgress';
import { LifeStageBadge } from '../components/camp/LifeStageBadge';

interface Companion {
  uuid: string;
  species: string;
  name: string | null;
  life_stage: string;
  health_status: number;
  bond_level: number;
  base_stats: Record<string, number>;
  mutated_stats: Record<string, number>;
  personality_type: string;
  personality_traits: string[];
  behavioral_quirks: string[];
}

interface CareState {
  hunger: number;
  energy: number;
  morale: number;
  cleanliness: number;
}

export function CampView() {
  const [companions, setCompanions] = useState<Companion[]>([]);
  const [selectedCompanion, setSelectedCompanion] = useState<string | null>(null);
  const [careState, setCareState] = useState<CareState | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchCompanions = async () => {
    const token = localStorage.getItem('tektribe-auth');
    if (!token) return;

    try {
      const auth = JSON.parse(token);
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/companions`, {
        headers: { Authorization: `Bearer ${auth.sessionToken}` },
      });

      if (response.ok) {
        const data = await response.json();
        setCompanions(data);
        if (data.length > 0 && !selectedCompanion) {
          setSelectedCompanion(data[0].uuid);
        }
      }
    } catch (err) {
      console.error('Failed to fetch companions:', err);
    }
  };

  const fetchCareState = async (uuid: string) => {
    const token = localStorage.getItem('tektribe-auth');
    if (!token) return;

    try {
      const auth = JSON.parse(token);
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/care/${uuid}`, {
        headers: { Authorization: `Bearer ${auth.sessionToken}` },
      });

      if (response.ok) {
        const data = await response.json();
        setCareState(data);
      }
    } catch (err) {
      console.error('Failed to fetch care state:', err);
    }
  };

  useEffect(() => {
    fetchCompanions();
  }, []);

  useEffect(() => {
    if (selectedCompanion) {
      fetchCareState(selectedCompanion);
    }
  }, [selectedCompanion]);

  const handleCareAction = async (action: string) => {
    if (!selectedCompanion) return;
    setLoading(true);
    try {
      const token = localStorage.getItem('tektribe-auth');
      if (!token) return;
      const auth = JSON.parse(token);
      await fetch(`${import.meta.env.VITE_API_URL}/api/care/${selectedCompanion}/${action}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${auth.sessionToken}` },
      });
      await fetchCareState(selectedCompanion);
    } catch (err) {
      console.error('Care action failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const companion = companions.find(c => c.uuid === selectedCompanion);

  if (companions.length === 0) {
    return (
      <div className="camp-view">
        <h1>Camp</h1>
        <p className="empty">No companions yet. Hatch an egg to begin!</p>
      </div>
    );
  }

  return (
    <div className="camp-view">
      <div className="camp-header">
        <h1>Camp</h1>
        <LifeStageBadge stage={companion?.life_stage || 'unknown'} />
      </div>

      <CompanionSelector
        companions={companions}
        selected={selectedCompanion}
        onSelect={setSelectedCompanion}
      />

      {companion && (
        <div className="camp-content">
          <div className="camp-left">
            <CompanionModel companion={companion} />
            <BondProgress bondLevel={companion.bond_level} />
          </div>

          <div className="camp-right">
            <CareMeters careState={careState} />
            <CareActions onAction={handleCareAction} disabled={loading} />
            <PersonalityCard companion={companion} />
            <StatsPanel companion={companion} />
          </div>
        </div>
      )}
    </div>
  );
}
