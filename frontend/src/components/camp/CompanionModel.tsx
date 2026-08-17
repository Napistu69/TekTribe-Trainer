interface Companion {
  uuid: string;
  species: string;
  name: string | null;
  life_stage: string;
}

interface CompanionModelProps {
  companion: Companion;
}

export function CompanionModel({ companion }: CompanionModelProps) {
  return (
    <div className="companion-model">
      <div className="model-canvas">
        <div className="companion-placeholder">
          <span className="species-icon">{companion.species.charAt(0).toUpperCase()}</span>
          <span className="life-stage">{companion.life_stage}</span>
        </div>
      </div>
      <h3>{companion.name || companion.species}</h3>
    </div>
  );
}
