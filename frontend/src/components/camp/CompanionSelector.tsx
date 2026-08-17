interface Companion {
  uuid: string;
  species: string;
  name: string | null;
  life_stage: string;
}

interface CompanionSelectorProps {
  companions: Companion[];
  selected: string | null;
  onSelect: (uuid: string) => void;
}

export function CompanionSelector({ companions, selected, onSelect }: CompanionSelectorProps) {
  return (
    <div className="companion-selector">
      {companions.map((c) => (
        <button
          key={c.uuid}
          className={`companion-select-btn ${selected === c.uuid ? 'selected' : ''}`}
          onClick={() => onSelect(c.uuid)}
        >
          <span className="species">{c.species}</span>
          {c.name && <span className="name">{c.name}</span>}
        </button>
      ))}
    </div>
  );
}
