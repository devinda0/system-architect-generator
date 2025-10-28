import { create } from 'zustand';
import type { Node, Edge } from '@xyflow/react';
import type { SystemContext } from '../types/architecture';


interface AppState {
  // Selected node for the left info panel
  selectedNode: Node | null;
  setSelectedNode: (node: Node | null) => void;

  currentContext: SystemContext | null;
  setCurrentContext: (context: SystemContext | null) => void;

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

  currentContext: null,
  setCurrentContext: (context) => {
    set({ currentContext: context });
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
