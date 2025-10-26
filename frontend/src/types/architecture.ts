// C4 Model Types based on the OOP Design document and Backend API compatibility

export interface Relationship {
  id?: string;
  source: string;
  target: string;
  description: string;
  type: 'uses' | 'contains' | 'depends_on' | 'communicates_with';
  properties?: {
    protocol?: string;
    data_format?: string;
    frequency?: string;
    [key: string]: any;
  };
}

export const ElementType = {
  SYSTEM_CONTEXT: 'system_context',
  CONTAINER: 'container',
  COMPONENT: 'component',
  EXTERNAL_ENTITY: 'external_entity',
} as const;

export type ElementType = (typeof ElementType)[keyof typeof ElementType];

export interface ArchitectureElement {
  id: string;
  name: string;
  description: string;
  type: ElementType;
  technology?: string;
  responsibilities?: string[];
  properties?: Record<string, any>;
  position?: {
    x: number;
    y: number;
  };
  metadata?: {
    color?: string;
    icon?: string;
    layer?: string;
    [key: string]: any;
  };
}

export interface SystemContext extends ArchitectureElement {
  type: typeof ElementType.SYSTEM_CONTEXT;
  purpose: string;
  external_entities: ExternalEntity[];
  business_context?: string;
  technical_context?: string;
}

export interface Container extends ArchitectureElement {
  type: typeof ElementType.CONTAINER;
  technology: string;
  responsibilities: string[];
  deployment?: {
    environment?: string;
    scaling?: string;
    resources?: Record<string, any>;
  };
}

export interface Component extends ArchitectureElement {
  type: typeof ElementType.COMPONENT;
  technology?: string;
  responsibilities: string[];
  layer: 'presentation' | 'business' | 'data' | 'infrastructure';
  interfaces?: ComponentInterface[];
  dependencies?: string[];
}

export interface ExternalEntity extends ArchitectureElement {
  type: typeof ElementType.EXTERNAL_ENTITY;
  entity_type: 'person' | 'system' | 'service' | 'database';
  interactions?: string[];
}

export interface ComponentInterface {
  name: string;
  type: 'http' | 'grpc' | 'message' | 'database';
  methods?: InterfaceMethod[];
}

export interface InterfaceMethod {
  name: string;
  description: string;
  parameters?: Parameter[];
  returns?: Parameter;
  errors?: ErrorResponse[];
}

export interface Parameter {
  name: string;
  type: string;
  description?: string;
  required?: boolean;
  default_value?: any;
}

export interface ErrorResponse {
  code: string | number;
  message: string;
  description?: string;
}

// React Flow node data
export interface NodeData {
  element: ArchitectureElement;
  label: string;
  description: string;
  technology?: string;
  responsibilities?: string[];
  isSelected?: boolean;
  isHighlighted?: boolean;
}

// Architecture Design
export interface ArchitectureDesign {
  id?: string;
  name: string;
  description?: string;
  system_context?: SystemContext;
  containers: Container[];
  components: Component[];
  external_entities: ExternalEntity[];
  relationships: Relationship[];
  design_rationale?: {
    overview: string;
    architectural_patterns: string[];
    key_decisions: Array<{
      decision: string;
      rationale: string;
    }>;
  };
  metadata?: {
    version?: string;
    author?: string;
    created_at?: string;
    updated_at?: string;
    tags?: string[];
    [key: string]: any;
  };
}

// Helper type guards
export function isSystemContext(element: ArchitectureElement): element is SystemContext {
  return element.type === ElementType.SYSTEM_CONTEXT;
}

export function isContainer(element: ArchitectureElement): element is Container {
  return element.type === ElementType.CONTAINER;
}

export function isComponent(element: ArchitectureElement): element is Component {
  return element.type === ElementType.COMPONENT;
}

export function isExternalEntity(element: ArchitectureElement): element is ExternalEntity {
  return element.type === ElementType.EXTERNAL_ENTITY;
}

// Utility functions for working with architecture elements
export function getAllElements(design: ArchitectureDesign): ArchitectureElement[] {
  const elements: ArchitectureElement[] = [];
  
  if (design.system_context) {
    elements.push(design.system_context);
  }
  
  elements.push(...design.containers);
  elements.push(...design.components);
  elements.push(...design.external_entities);
  
  return elements;
}

export function findElementById(design: ArchitectureDesign, id: string): ArchitectureElement | undefined {
  return getAllElements(design).find(element => element.id === id);
}

export function getElementsByType(design: ArchitectureDesign, type: ElementType): ArchitectureElement[] {
  return getAllElements(design).filter(element => element.type === type);
}

export function getRelationshipsForElement(design: ArchitectureDesign, elementId: string): Relationship[] {
  return design.relationships.filter(rel => 
    rel.source === elementId || rel.target === elementId
  );
}
