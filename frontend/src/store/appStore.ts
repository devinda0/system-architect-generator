import { create } from 'zustand';
import type { Node, Edge } from '@xyflow/react';


interface AppState {
  // Selected node for the left info panel
  selectedNode: Node | null;
  setSelectedNode: (node: Node | null) => void;

  // React Flow nodes and edges
  nodes: Node[];
  edges: Edge[];
  setNodes: (nodes: Node[]) => void;
  setEdges: (edges: Edge[]) => void;

  // Chat messages
  messages: { role: 'user' | 'assistant'; content: string }[];
  addMessage: (role: 'user' | 'assistant', content: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  selectedNode: null,
  setSelectedNode: (node) => {
    set({ selectedNode: node });
  },

  nodes: [],
  edges: [],
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),

  messages: [],
  addMessage: (role, content) =>
    set((state) => ({
      messages: [...state.messages, { role, content }],
    })),
}));
