import { useDialogueStore } from '../../stores/dialogueStore';
import { OverseerAvatar } from './OverseerAvatar';

export function OverseerDialog() {
  const { currentDialogue, currentNodeIndex, isVisible, nextNode, closeDialogue } = useDialogueStore();
  
  if (!isVisible || !currentDialogue) return null;
  
  const nodes = currentDialogue.nodes || [];
  const currentNode = nodes[currentNodeIndex];
  
  if (!currentNode) return null;
  
  return (
    <div className="overseer-dialog-overlay">
      <div className="overseer-dialog-card">
        <button className="dialog-close" onClick={closeDialogue}>
          ✕
        </button>
        
        <div className="dialog-portrait">
          <OverseerAvatar size="large" animated />
        </div>
        
        <div className="dialog-content">
          <span className="dialog-speaker">{currentNode.speaker}</span>
          <p className="dialog-text">{currentNode.text}</p>
        </div>
        
        <div className="dialog-choices">
          {currentNode.choices?.map((choice: any, index: number) => (
            <button
              key={index}
              className="dialog-choice"
              onClick={nextNode}
            >
              {choice.text}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
