import type {
  SystemContext,
} from '../types/architecture';
import { ElementType } from '../types/architecture';

/**
 * Create a sample architecture tree for testing
 */
export function createSampleArchitecture(): SystemContext {
  return {
    id: 'system-1',
    name: 'AI-Powered Software Engineering Workbench',
    description: 'A comprehensive platform for generating and managing software architecture',
    type: ElementType.SYSTEM_CONTEXT,
    relationships: [],
    children: [
      {
        id: 'container-1',
        name: 'Frontend Application',
        description: 'React-based web application for architecture visualization',
        type: ElementType.CONTAINER,
        technology: 'React + TypeScript + Vite',
        relationships: [
          {
            targetId: 'container-2',
            description: 'Sends API requests to',
          },
        ],
        children: [
          {
            id: 'component-1',
            name: 'Canvas Component',
            description: 'Interactive canvas for visualizing C4 diagrams',
            type: ElementType.COMPONENT,
            technology: 'React Flow',
            relationships: [],
          },
          {
            id: 'component-2',
            name: 'Chat Panel',
            description: 'AI chat interface for architecture discussions',
            type: ElementType.COMPONENT,
            technology: 'React + Zustand',
            relationships: [
              {
                targetId: 'component-4',
                description: 'Sends chat messages to',
              },
            ],
          },
          {
            id: 'component-3',
            name: 'Node Drawer',
            description: 'Detail panel for node information and actions',
            type: ElementType.COMPONENT,
            technology: 'React',
            relationships: [],
          },
        ],
      },
      {
        id: 'container-2',
        name: 'Backend API',
        description: 'FastAPI server for handling AI operations',
        type: ElementType.CONTAINER,
        technology: 'FastAPI + Python',
        relationships: [
          {
            targetId: 'container-3',
            description: 'Queries knowledge from',
          },
        ],
        children: [
          {
            id: 'component-4',
            name: 'Chat Service',
            description: 'Handles chat interactions with AI',
            type: ElementType.COMPONENT,
            technology: 'LangChain',
            relationships: [],
          },
          {
            id: 'component-5',
            name: 'Design Engine',
            description: 'Core AI engine for architecture generation',
            type: ElementType.COMPONENT,
            technology: 'LangChain + Gemini',
            relationships: [],
          },
          {
            id: 'component-6',
            name: 'Project Controller',
            description: 'Manages project CRUD operations',
            type: ElementType.COMPONENT,
            technology: 'FastAPI',
            relationships: [],
          },
        ],
      },
      {
        id: 'container-3',
        name: 'Knowledge Base',
        description: 'Hybrid vector and relational database',
        type: ElementType.CONTAINER,
        technology: 'ChromaDB + PostgreSQL',
        relationships: [],
        children: [
          {
            id: 'component-7',
            name: 'Vector Store',
            description: 'Stores embeddings for RAG',
            type: ElementType.COMPONENT,
            technology: 'ChromaDB',
            relationships: [],
          },
          {
            id: 'component-8',
            name: 'Metadata Store',
            description: 'Stores structured metadata',
            type: ElementType.COMPONENT,
            technology: 'PostgreSQL',
            relationships: [],
          },
        ],
      },
    ],
  };
}
