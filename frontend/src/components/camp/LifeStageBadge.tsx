interface LifeStageBadgeProps {
  stage: string;
}

const STAGE_LABELS: Record<string, string> = {
  egg: 'Egg',
  hatchling: 'Hatchling',
  juvenile: 'Juvenile',
  adult: 'Adult',
  elder: 'Elder',
};

export function LifeStageBadge({ stage }: LifeStageBadgeProps) {
  return (
    <span className={`life-stage-badge stage-${stage}`}>
      {STAGE_LABELS[stage] || stage}
    </span>
  );
}
