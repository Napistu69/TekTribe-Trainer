import { useEffect, useState } from 'react';

interface ForgeOption {
  id: string;
  input_currency: string;
  input_amount: number;
  output_currency: string;
  output_amount: number;
}

interface ForgeResult {
  success: boolean;
  refinement_type: string;
  input_currency: string;
  input_amount: number;
  output_currency: string;
  output_amount: number;
  times: number;
  new_balances: {
    dust: number;
    shard: number;
    cuboid: number;
    ele: number;
  };
}

const REFINEMENT_LABELS: Record<string, string> = {
  dust_to_shard: 'Dust → Shard',
  shard_to_cuboid: 'Shard → Cuboid',
  cuboid_to_ele: 'Cuboid → $ELE',
};

const CURRENCY_IMAGES: Record<string, string> = {
  dust: '/assets/Currency & Resource/ELE_Dust_20.png',
  shard: '/assets/Currency & Resource/ELE_Shard_20.png',
  cuboid: '/assets/Currency & Resource/ELE_Cuboid_20.png',
  ele: '/assets/Currency & Resource/ELE_20.png',
};

export function ForgeView() {
  const [options, setOptions] = useState<ForgeOption[]>([]);
  const [selectedOption, setSelectedOption] = useState<string>('dust_to_shard');
  const [times, setTimes] = useState<number>(1);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ForgeResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchOptions();
  }, []);

  const getToken = () => {
    const match = document.cookie.match(/session_token=([^;]+)/);
    return match ? match[1].replace('Bearer%20', '') : '';
  };

  const fetchOptions = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/forge/options`);
      const data = await response.json();
      setOptions(data);
    } catch (err) {
      setError('Failed to load refinement options');
    }
  };

  const handleRefine = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const token = getToken();
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/forge/refine`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          refinement_type: selectedOption,
          times,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || 'Refinement failed');
      } else {
        setResult(data);
      }
    } catch (err: any) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  const selected = options.find(o => o.id === selectedOption);

  return (
    <div className="forge-view">
      <h1>Forge</h1>
      <p className="forge-description">
        Refine your currency into higher tiers. The forge converts Dust into Shards, Shards into Cuboids, and Cuboids into $ELE.
      </p>

      <div className="forge-options">
        {options.map(option => (
          <button
            key={option.id}
            className={`forge-option ${selectedOption === option.id ? 'selected' : ''}`}
            onClick={() => setSelectedOption(option.id)}
          >
            <div className="forge-option-header">
              <img src={CURRENCY_IMAGES[option.input_currency]} alt={option.input_currency} className="currency-icon" />
              <span className="forge-arrow">→</span>
              <img src={CURRENCY_IMAGES[option.output_currency]} alt={option.output_currency} className="currency-icon" />
            </div>
            <div className="forge-option-label">{REFINEMENT_LABELS[option.id] || option.id}</div>
            <div className="forge-option-rate">
              {option.input_amount} {option.input_currency} = {option.output_amount} {option.output_currency}
            </div>
          </button>
        ))}
      </div>

      {selected && (
        <div className="forge-refine-panel">
          <h3>Refine {REFINEMENT_LABELS[selected.id]}</h3>
          <div className="forge-calc">
            <div className="forge-calc-row">
              <span>Input:</span>
              <span>{selected.input_amount * times} {selected.input_currency}</span>
            </div>
            <div className="forge-calc-row">
              <span>Output:</span>
              <span>{selected.output_amount * times} {selected.output_currency}</span>
            </div>
          </div>

          <div className="forge-times">
            <label>Times:</label>
            <input
              type="number"
              min={1}
              max={100}
              value={times}
              onChange={e => setTimes(Math.max(1, Math.min(100, parseInt(e.target.value) || 1)))}
            />
          </div>

          <button
            className="btn-primary forge-refine-btn"
            onClick={handleRefine}
            disabled={loading}
          >
            {loading ? 'Refining...' : 'Refine'}
          </button>
        </div>
      )}

      {result && (
        <div className="forge-result">
          <h4>Refinement Complete!</h4>
          <p>
            Converted {result.input_amount} {result.input_currency} into {result.output_amount} {result.output_currency}
          </p>
        </div>
      )}

      {error && <div className="forge-error">{error}</div>}
    </div>
  );
}
