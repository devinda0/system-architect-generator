// C4 Model Types based on the OOP Design document

export interface Relationship {
  targetId: string;
  description: string;
}

export const ElementType = {
  SYSTEM_CONTEXT: 'SystemContext',
  CONTAINER: 'Container',
  COMPONENT: 'Component',
} as const;

export type ElementType = (typeof ElementType)[keyof typeof ElementType];

export interface ArchitectureElement {
  id: string;
  name: string;
  description: string;
  type: ElementType;
  relationships: Relationship[];
}

export interface SystemContext extends ArchitectureElement {
  type: typeof ElementType.SYSTEM_CONTEXT;
  children: Container[];
}

export interface Container extends ArchitectureElement {
  type: typeof ElementType.CONTAINER;
  technology?: string;
  children: Component[];
}

export interface Component extends ArchitectureElement {
  type: typeof ElementType.COMPONENT;
  technology?: string;
  children?: any[]; // Can be extended for code elements
}

// React Flow node data
export interface NodeData {
  element: ArchitectureElement;
  label: string;
  description: string;
  technology?: string;
}
