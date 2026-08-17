interface Companion {
  personality_type: string;
  personality_traits: string[];
  behavioral_quirks: string[];
}

interface PersonalityCardProps {
  companion: Companion;
}

export function PersonalityCard({ companion }: PersonalityCardProps) {
  return (
    <div className="personality-card">
      <h4>Personality</h4>
      <span className="personality-type">{companion.personality_type}</span>
      <div className="traits">
        {companion.personality_traits.map((t) => (
          <span key={t} className="trait">{t}</span>
        ))}
      </div>
      <div className="quirks">
        {companion.behavioral_quirks.map((q) => (
          <span key={q} className="quirk">{q}</span>
        ))}
      </div>
    </div>
  );
}
