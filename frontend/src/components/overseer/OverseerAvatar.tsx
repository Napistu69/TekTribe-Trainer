interface OverseerAvatarProps {
  size?: 'small' | 'medium' | 'large';
  animated?: boolean;
}

export function OverseerAvatar({ size = 'medium', animated = true }: OverseerAvatarProps) {
  const sizeClass = `avatar-${size}`;
  const animClass = animated ? 'animated' : '';
  
  return (
    <div className={`overseer-avatar ${sizeClass} ${animClass}`}>
      <div className="avatar-glow" />
      <div className="avatar-core" />
    </div>
  );
}
