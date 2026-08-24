import { useState, useRef, useEffect } from 'react';

interface KnowledgeEntry {
  id: string;
  title: string;
  content: string;
  category: string;
}

const SAMPLE_KNOWLEDGE: KnowledgeEntry[] = [
  {
    id: '1',
    title: 'The Zero Point',
    content: 'Green is the Zero Point on the visible spectrum. The midpoint between Infrared (positive) and Ultraviolet (negative). Human peak visual sensitivity at approximately 550 nanometers — green-yellow.',
    category: 'Spectral',
  },
  {
    id: '2',
    title: 'The Overseer\'s Iris',
    content: 'The emerald green iris of the Overseer is the literal Zero Point frequency — 532 nanometers — the wavelength of sharpest perception. The Observer fixed at the neutral anchor.',
    category: 'Overseer',
  },
  {
    id: '3',
    title: 'Infrared Perception',
    content: 'The human body emits infrared. The earth emits infrared. The spirit world at the positive end has always been there. We have simply been tuned away from it.',
    category: 'Perception',
  },
  {
    id: '4',
    title: 'The Emerald Tablet',
    content: 'Emerald green IS the Zero Point frequency. The Tablet was not named for its material color arbitrarily. It was named for the frequency it encodes.',
    category: 'Artifacts',
  },
  {
    id: '5',
    title: 'Natural Law',
    content: 'Materials that breathe, age, decompose, and regenerate. Natural Law expressed visually through earthy greens, patina copper, warm browns, soft stone.',
    category: 'Doctrine',
  },
];

export function OverseerView() {
  const [selectedEntry, setSelectedEntry] = useState<KnowledgeEntry | null>(null);
  const [isReading, setIsReading] = useState(false);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const handleReadAloud = (entry: KnowledgeEntry) => {
    if (isReading) return;
    
    setSelectedEntry(entry);
    setIsReading(true);
    
    // Simulate reading delay
    setTimeout(() => {
      if (mountedRef.current) setIsReading(false);
    }, 3000);
  };

  return (
    <div className="overseer-view">
      <div className="overseer-header">
        <img
          src="/assets/Overseer & Lore/overseer.png"
          alt="Overseer"
          className="overseer-portrait"
        />
        <h1>Akashic Research Oracle</h1>
        <p className="overseer-subtitle">Knowledge from the digital ether</p>
      </div>

      {isReading && selectedEntry && (
        <div className="oracle-reading">
          <div className="oracle-glow"></div>
          <p className="oracle-text">{selectedEntry.content}</p>
        </div>
      )}

      <div className="knowledge-list">
        {SAMPLE_KNOWLEDGE.map(entry => (
          <div
            key={entry.id}
            className={`knowledge-card ${selectedEntry?.id === entry.id ? 'active' : ''}`}
            onClick={() => handleReadAloud(entry)}
          >
            <div className="knowledge-header">
              <h3>{entry.title}</h3>
              <span className="knowledge-category">{entry.category}</span>
            </div>
            <p className="knowledge-preview">{entry.content.substring(0, 80)}...</p>
            <button 
              className="btn-secondary read-btn"
              disabled={isReading}
            >
              {isReading && selectedEntry?.id === entry.id ? 'Reading...' : 'Read'}
            </button>
          </div>
        ))}
      </div>

      <div className="oracle-footer">
        <p>More knowledge entries will be revealed as the Oracle grows...</p>
      </div>
    </div>
  );
}
