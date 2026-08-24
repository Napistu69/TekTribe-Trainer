import { useState } from 'react';
import { TutorialOverlay, useTutorial } from '../components/shared/TutorialOverlay';

const TUTORIAL_STEPS = [
  { title: 'Akashic Research Oracle', text: 'The Overseer guards the knowledge of the old world. Click on any entry to read it.' },
  { title: 'Knowledge Tidbits', text: 'Each entry reveals a piece of the TekTribe doctrine — spectral perception, natural law, and the history of the Overseer.' },
  { title: 'Future Revelations', text: 'More knowledge entries will be revealed as the Oracle grows. Return often to discover new insights.' },
];

const SAMPLE_KNOWLEDGE = [
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
  const [selectedEntry, setSelectedEntry] = useState<typeof SAMPLE_KNOWLEDGE[0] | null>(null);
  const { showTutorial, completeTutorial } = useTutorial('tutorial-overseer');

  return (
    <div className="overseer-view">
      {showTutorial && <TutorialOverlay steps={TUTORIAL_STEPS} storageKey="tutorial-overseer" onComplete={completeTutorial} />}
      
      <div className="overseer-header">
        <img src="/assets/Overseer & Lore/overseer.png" alt="Overseer" className="overseer-portrait" />
        <h1>Akashic Research Oracle</h1>
        <p className="overseer-subtitle">Knowledge from the digital ether</p>
      </div>

      {selectedEntry && (
        <div className="oracle-reading">
          <div className="oracle-glow"></div>
          <h4 className="oracle-title">{selectedEntry.title}</h4>
          <p className="oracle-text">{selectedEntry.content}</p>
          <span className="oracle-category">{selectedEntry.category}</span>
        </div>
      )}

      <div className="knowledge-list">
        {SAMPLE_KNOWLEDGE.map(entry => (
          <div
            key={entry.id}
            className={`knowledge-card ${selectedEntry?.id === entry.id ? 'active' : ''}`}
            onClick={() => setSelectedEntry(entry)}
          >
            <div className="knowledge-header">
              <h3>{entry.title}</h3>
              <span className="knowledge-category">{entry.category}</span>
            </div>
            <p className="knowledge-preview">{entry.content.substring(0, 80)}...</p>
            <button className="btn-secondary read-btn" onClick={(e) => { e.stopPropagation(); setSelectedEntry(entry); }}>
              {selectedEntry?.id === entry.id ? 'Reading' : 'Read'}
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
