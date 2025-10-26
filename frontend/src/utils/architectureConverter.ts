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
    purpose: 'Provide AI-powered architecture generation and management capabilities',
    external_entities: [
      {
        id: 'user-1',
        name: 'Software Architect',
        description: 'Uses the system to design and manage software architectures',
        type: ElementType.EXTERNAL_ENTITY,
        entity_type: 'person',
        interactions: ['Creates projects', 'Generates architectures', 'Reviews designs'],
      },
    ],
  };
}

/**
 * Convert architecture data to React Flow format
 */
export function convertToReactFlowFormat(architecture: SystemContext): { nodes: any[], edges: any[] } {
  const nodes: any[] = [];
  const edges: any[] = [];

  // Add system context as main node
  nodes.push({
    id: architecture.id,
    type: 'custom',
    position: { x: 0, y: 0 },
    data: {
      label: architecture.name,
      description: architecture.description,
      elementType: architecture.type,
    },
  });

  // Add external entities
  architecture.external_entities?.forEach((entity, index) => {
    nodes.push({
      id: entity.id,
      type: 'custom',
      position: { x: -200, y: index * 100 },
      data: {
        label: entity.name,
        description: entity.description,
        elementType: entity.type,
      },
    });

    // Add edge from external entity to system
    edges.push({
      id: `${entity.id}-${architecture.id}`,
      source: entity.id,
      target: architecture.id,
      type: 'smoothstep',
    });
  });

  return { nodes, edges };
}
