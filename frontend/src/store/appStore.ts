import { create } from 'zustand';
import type { Node, Edge } from '@xyflow/react';
import type { ArchitectureElement } from '../types/architecture';

interface AppState {
  // Selected node for the drawer
  selectedNode: Node | null;
  setSelectedNode: (node: Node | null) => void;

  // Drawer state
  isDrawerOpen: boolean;
  setIsDrawerOpen: (isOpen: boolean) => void;

  // Architecture elements
  architectureElements: ArchitectureElement[];
  setArchitectureElements: (elements: ArchitectureElement[]) => void;

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
    set({ selectedNode: node, isDrawerOpen: !!node });
  },

  isDrawerOpen: false,
  setIsDrawerOpen: (isOpen) => set({ isDrawerOpen: isOpen }),

  architectureElements: [],
  setArchitectureElements: (elements) => set({ architectureElements: elements }),

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
