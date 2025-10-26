// API Response Types
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  status?: string;
  errors?: string[];
}

// Pagination Types
export interface PaginationParams {
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Architecture Element Types
export interface ArchitectureElement {
  id: string;
  name: string;
  type: 'system_context' | 'container' | 'component' | 'external_entity';
  description: string;
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

export interface ArchitectureRelationship {
  id: string;
  source: string;
  target: string;
  type: 'uses' | 'contains' | 'depends_on' | 'communicates_with';
  description: string;
  properties?: {
    protocol?: string;
    data_format?: string;
    frequency?: string;
    [key: string]: any;
  };
}

export interface ArchitectureDesign {
  id?: string;
  name: string;
  description?: string;
  elements: ArchitectureElement[];
  relationships: ArchitectureRelationship[];
  metadata?: {
    version?: string;
    author?: string;
    created_at?: string;
    updated_at?: string;
    tags?: string[];
    [key: string]: any;
  };
}

// System Context Types
export interface SystemContext {
  name: string;
  description: string;
  purpose: string;
  external_entities: ExternalEntity[];
  business_context?: string;
  technical_context?: string;
}

export interface ExternalEntity {
  name: string;
  description: string;
  type: 'person' | 'system' | 'service' | 'database';
  interactions?: string[];
}

// Container Types
export interface Container {
  name: string;
  description: string;
  technology: string;
  responsibilities: string[];
  type: 'web_app' | 'mobile_app' | 'api' | 'database' | 'message_queue' | 'service';
  deployment?: {
    environment?: string;
    scaling?: string;
    resources?: Record<string, any>;
  };
}

// Component Types
export interface Component {
  name: string;
  description: string;
  type: 'controller' | 'service' | 'repository' | 'model' | 'utility' | 'middleware';
  responsibilities: string[];
  layer: 'presentation' | 'business' | 'data' | 'infrastructure';
  interfaces?: ComponentInterface[];
  dependencies?: string[];
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

// Design Pattern Types
export interface DesignPattern {
  name: string;
  description: string;
  application: string;
  components_involved: string[];
  benefits?: string[];
  trade_offs?: string[];
}

// Technology Types
export interface TechnologySuggestion {
  technology: string;
  category: 'language' | 'framework' | 'database' | 'message_queue' | 'cache' | 'tool';
  rationale: string;
  pros: string[];
  cons: string[];
  complexity: 'low' | 'medium' | 'high';
  maturity: 'experimental' | 'stable' | 'mature';
  learning_curve: 'easy' | 'moderate' | 'steep';
}

// Quality Attributes
export interface QualityAttribute {
  name: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  measures?: QualityMeasure[];
  constraints?: string[];
}

export interface QualityMeasure {
  metric: string;
  target_value: string | number;
  measurement_method?: string;
}

// Decision Record Types
export interface ArchitecturalDecision {
  id: string;
  title: string;
  status: 'proposed' | 'accepted' | 'deprecated' | 'superseded';
  context: string;
  decision: string;
  rationale: string;
  consequences: string[];
  alternatives?: {
    option: string;
    reason_rejected: string;
  }[];
  date: string;
  author?: string;
}

// Validation Types
export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  suggestions?: string[];
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
  severity: 'error' | 'warning' | 'info';
}

export interface ValidationWarning {
  field: string;
  message: string;
  code: string;
  suggestion?: string;
}

// Export Types
export interface ExportOptions {
  format: 'json' | 'yaml' | 'markdown' | 'svg' | 'png' | 'pdf';
  include_metadata?: boolean;
  include_relationships?: boolean;
  template?: string;
}

export interface ExportResult {
  content: string | Blob;
  filename: string;
  format: string;
  size?: number;
}