import type { SystemContext } from '../types/architecture';

export function renderSystemContextDiagram(context: SystemContext): { nodes: any[], edges: any[] } {
  const nodes: any[] = [];
  const edges: any[] = [];

  // System Context node (main system)
  nodes.push({
    id: context.id,
    type: 'customContainer',
    position: { x: 400, y: 100 },
    data: {
      label: context.name,
      description: context.description,
      elementType: context.type,
      technology: '',
    },
    style: { width: 800, height: 600 },
  });

  // External entities
  let entityY = 100;
  context.external_entities.forEach((entity) => {
    nodes.push({
      id: entity.id,
      type: 'customActor',
      position: { x: 50, y: entityY },
      data: {
        label: entity.name,
        description: entity.description,
        elementType: entity.type,
        technology: '',
      },
      style: { width: 150, height: 100 },
    });

    // Connect external entity to system
    edges.push({
      id: `${entity.id}-${context.id}`,
      source: entity.id,
      target: context.id,
      type: 'smoothstep',
      animated: true,
    });

    entityY += 150;
  });

  return { nodes, edges };
}
