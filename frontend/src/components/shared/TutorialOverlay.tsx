import { useState } from 'react';

interface TutorialStep {
  title: string;
  text: string;
}

interface TutorialOverlayProps {
  steps: TutorialStep[];
  storageKey: string;
  onComplete: () => void;
}

export function TutorialOverlay({ steps, storageKey, onComplete }: TutorialOverlayProps) {
  const [step, setStep] = useState(0);

  const handleNext = () => {
    if (step < steps.length - 1) {
      setStep(step + 1);
    } else {
      localStorage.setItem(storageKey, 'true');
      onComplete();
    }
  };

  const handleSkip = () => {
    localStorage.setItem(storageKey, 'true');
    onComplete();
  };

  const current = steps[step];

  return (
    <div className="tutorial-overlay">
      <div className="tutorial-card">
        <h3>{current.title}</h3>
        <p>{current.text}</p>
        <div className="tutorial-actions">
          <button className="btn-primary" onClick={handleNext}>
            {step < steps.length - 1 ? 'Next' : 'Got it!'}
          </button>
          <button className="btn-secondary" onClick={handleSkip}>Skip</button>
        </div>
        <div className="tutorial-dots">
          {steps.map((_, i) => (
            <span key={i} className={`dot ${i === step ? 'active' : ''}`} />
          ))}
        </div>
      </div>
    </div>
  );
}

export function useTutorial(storageKey: string) {
  const [showTutorial, setShowTutorial] = useState(() => {
    return localStorage.getItem(storageKey) !== 'true';
  });

  const completeTutorial = () => {
    localStorage.setItem(storageKey, 'true');
    setShowTutorial(false);
  };

  return { showTutorial, completeTutorial };
}
