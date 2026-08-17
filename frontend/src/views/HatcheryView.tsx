import { useState, useEffect } from 'react';
import { EggShelf } from '../components/hatchery/EggShelf';
import { IncubatorControls } from '../components/hatchery/IncubatorControls';
import { HatchButton } from '../components/hatchery/HatchButton';
import { PullEggButton } from '../components/hatchery/PullEggButton';

interface Egg {
  uuid: string;
  rarity: string;
  source: string;
  pulled_at: string;
  incubation_started_at: string | null;
  temperature: number;
  stability: number;
}

export function HatcheryView() {
  const [eggs, setEggs] = useState<Egg[]>([]);
  const [selectedEgg, setSelectedEgg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  
  const fetchEggs = async () => {
    const token = localStorage.getItem('tektribe-auth');
    if (!token) return;
    
    try {
      const auth = JSON.parse(token);
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/eggs`, {
        headers: { Authorization: `Bearer ${auth.sessionToken}` },
      });
      
      if (response.ok) {
        const data = await response.json();
        setEggs(data);
      }
    } catch (err) {
      console.error('Failed to fetch eggs:', err);
    }
  };
  
  useEffect(() => {
    fetchEggs();
    const interval = setInterval(fetchEggs, 30000);
    return () => clearInterval(interval);
  }, []);
  
  const handlePullEgg = async () => {
    const token = localStorage.getItem('tektribe-auth');
    if (!token) return;
    
    setLoading(true);
    try {
      const auth = JSON.parse(token);
      await fetch(`${import.meta.env.VITE_API_URL}/api/eggs/pull`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${auth.sessionToken}` },
      });
      await fetchEggs();
    } catch (err) {
      console.error('Failed to pull egg:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleHatch = async (eggUuid: string) => {
    const token = localStorage.getItem('tektribe-auth');
    if (!token) return;
    
    setLoading(true);
    try {
      const auth = JSON.parse(token);
      await fetch(`${import.meta.env.VITE_API_URL}/api/eggs/${eggUuid}/hatch`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${auth.sessionToken}` },
      });
      await fetchEggs();
      setSelectedEgg(null);
    } catch (err) {
      console.error('Failed to hatch egg:', err);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="hatchery-view">
      <div className="hatchery-header">
        <h1>Hatchery</h1>
        <PullEggButton onClick={handlePullEgg} loading={loading} />
      </div>
      
      <EggShelf
        eggs={eggs}
        selectedEgg={selectedEgg}
        onSelectEgg={setSelectedEgg}
      />
      
      {selectedEgg && (
        <div className="incubator-section">
          <IncubatorControls egg={eggs.find(e => e.uuid === selectedEgg)} />
          <HatchButton
            egg={eggs.find(e => e.uuid === selectedEgg)}
            onHatch={() => handleHatch(selectedEgg)}
            loading={loading}
          />
        </div>
      )}
    </div>
  );
}
