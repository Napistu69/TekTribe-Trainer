import { create } from 'zustand';

interface DialogueState {
  currentDialogue: any | null;
  currentNodeIndex: number;
  isVisible: boolean;
  
  showDialogue: (dialogue: any) => void;
  nextNode: () => void;
  closeDialogue: () => void;
}

export const useDialogueStore = create<DialogueState>()((set) => ({
  currentDialogue: null,
  currentNodeIndex: 0,
  isVisible: false,
  
  showDialogue: (dialogue) => set({
    currentDialogue: dialogue,
    currentNodeIndex: 0,
    isVisible: true,
  }),
  
  nextNode: () => set((state) => {
    if (!state.currentDialogue) return state;
    
    const nodes = state.currentDialogue.nodes || [];
    const currentNode = nodes[state.currentNodeIndex];
    
    // If there's a next node, go to it
    if (currentNode?.choices?.[0]?.next) {
      const nextIndex = nodes.findIndex((n: any) => n.id === currentNode.choices[0].next);
      if (nextIndex !== -1) {
        return { currentNodeIndex: nextIndex };
      }
    }
    
    // Otherwise close
    return {
      currentDialogue: null,
      currentNodeIndex: 0,
      isVisible: false,
    };
  }),
  
  closeDialogue: () => set({
    currentDialogue: null,
    currentNodeIndex: 0,
    isVisible: false,
  }),
}));
