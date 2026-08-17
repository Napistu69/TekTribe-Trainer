interface ActiveExpeditionsProps {
  expeditions: any[];
  onCollect: (expeditionUuid: string) => void;
}

export function ActiveExpeditions({ expeditions, onCollect }: ActiveExpeditionsProps) {
  const getCountdown = (returnsAt: string) => {
    const diff = new Date(returnsAt).getTime() - Date.now();
    if (diff <= 0) return 'Ready!';
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    return `${hours}h ${minutes}m`;
  };
  
  if (expeditions.length === 0) {
    return (
      <div className="active-expeditions">
        <h3>Active Expeditions</h3>
        <p className="empty">No active expeditions. Dispatch a companion to explore!</p>
      </div>
    );
  }
  
  return (
    <div className="active-expeditions">
      <h3>Active Expeditions</h3>
      {expeditions.map((exp) => {
        const ready = new Date(exp.returns_at).getTime() <= Date.now();
        return (
          <div key={exp.uuid} className={`expedition-item ${ready ? 'ready' : ''}`}>
            <div className="expedition-info">
              <span className="biome">{exp.biome_zone.replace('_', ' ')}</span>
              <span className={ready ? 'countdown ready-text' : 'countdown'}>
                {ready ? '✨ Ready!' : getCountdown(exp.returns_at)}
              </span>
            </div>
            {ready && (
              <button className="btn-small" onClick={() => onCollect(exp.uuid)}>
                Collect
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}
