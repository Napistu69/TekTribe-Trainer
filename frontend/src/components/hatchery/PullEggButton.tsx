interface PullEggButtonProps {
  onClick: () => void;
  loading: boolean;
}

export function PullEggButton({ onClick, loading }: PullEggButtonProps) {
  return (
    <button
      className="btn-primary pull-egg-btn"
      onClick={onClick}
      disabled={loading}
    >
      {loading ? 'Pulling...' : 'Pull Egg'}
    </button>
  );
}
