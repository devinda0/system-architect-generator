import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';

// Design Engine Types
export interface InitialDesignRequest {
  requirements: string;
}

export interface InitialDesignResponse {
  system_context: {
    name: string;
    description: string;
    purpose: string;
    external_entities: Array<{
      name: string;
      description: string;
      type: string;
    }>;
  };
  containers: Array<{
    name: string;
    description: string;
    technology: string;
    responsibilities: string[];
    type: string;
  }>;
  relationships: Array<{
    source: string;
    target: string;
    description: string;
    type: string;
  }>;
  design_rationale: {
    overview: string;
    architectural_patterns: string[];
    key_decisions: Array<{
      decision: string;
      rationale: string;
    }>;
  };
}

export interface TechSuggestionRequest {
  element_name: string;
  element_type: string;
  element_description: string;
  element_context?: any;
}

export interface TechSuggestionResponse {
  element_name: string;
  element_type: string;
  primary_recommendation: {
    technology: string;
    rationale: string;
    implementation_guidance: string[];
    pros_cons: {
      pros: string[];
      cons: string[];
    };
  };
  alternatives: Array<{
    technology: string;
    rationale: string;
    pros_cons: {
      pros: string[];
      cons: string[];
    };
  }>;
  integration_considerations: string[];
}

export interface DecompositionRequest {
  container_name: string;
  container_type: string;
  container_description: string;
  container_context?: any;
}

export interface DecompositionResponse {
  container_name: string;
  components: Array<{
    name: string;
    description: string;
    type: string;
    responsibilities: string[];
    layer: string;
  }>;
  component_relationships: Array<{
    source: string;
    target: string;
    description: string;
    type: string;
  }>;
  internal_flows: Array<{
    name: string;
    description: string;
    steps: Array<{
      step: number;
      component: string;
      action: string;
    }>;
  }>;
  design_patterns: Array<{
    pattern: string;
    application: string;
    components_involved: string[];
  }>;
}

export interface APISuggestionRequest {
  component_name: string;
  component_type: string;
  component_description: string;
  component_responsibilities: string[];
  component_context?: any;
}

export interface APISuggestionResponse {
  component_name: string;
  suggested_endpoints: Array<{
    method: string;
    path: string;
    description: string;
    request_schema?: any;
    response_schema?: any;
    error_responses?: Array<{
      status_code: number;
      description: string;
    }>;
  }>;
  authentication_scheme?: {
    type: string;
    description: string;
  };
  rate_limiting?: {
    strategy: string;
    limits: any;
  };
  error_handling_patterns: string[];
  api_documentation_notes: string[];
}

export interface RefactorRequest {
  element_name: string;
  element_type: string;
  element_description: string;
  refactoring_goal: string;
  element_context?: any;
}

export interface RefactorResponse {
  element_name: string;
  refactoring_suggestions: Array<{
    suggestion: string;
    rationale: string;
    impact: string;
    effort_estimate: string;
  }>;
  updated_element?: {
    name: string;
    description: string;
    changes: string[];
  };
  additional_elements?: Array<{
    name: string;
    description: string;
    type: string;
    rationale: string;
  }>;
  migration_steps?: Array<{
    step: number;
    description: string;
    considerations: string[];
  }>;
}

export interface EngineInfoResponse {
  name: string;
  version: string;
  supported_features: string[];
  rag_enabled: boolean;
  available_models: string[];
}

export interface AIActionRequest {
  action_type: string;
  target_element?: string;
  parameters: any;
  context?: any;
}

export interface AIActionResponse {
  action_type: string;
  result: any;
  suggestions?: string[];
  updates?: any;
}

export interface ElementUpdateRequest {
  element_id: string;
  updates: any;
}

export interface ElementUpdateResponse {
  element_id: string;
  updated_properties: any;
  validation_results: any;
}

export interface DesignTreeResponse {
  tree_structure: any;
  metadata: any;
}

class DesignService {
  /**
   * Generate initial system design from requirements
   */
  async generateInitialDesign(requirements: string): Promise<InitialDesignResponse> {
    try {
      const response = await apiClient.post<InitialDesignResponse>(
        API_ENDPOINTS.GENERATE_INITIAL_DESIGN,
        { requirements }
      );
      return response;
    } catch (error) {
      console.error('Generate initial design error:', error);
      throw error;
    }
  }

  /**
   * Get technology suggestions for an element
   */
  async suggestTechnology(request: TechSuggestionRequest): Promise<TechSuggestionResponse> {
    try {
      const response = await apiClient.post<TechSuggestionResponse>(
        API_ENDPOINTS.SUGGEST_TECHNOLOGY,
        request
      );
      return response;
    } catch (error) {
      console.error('Suggest technology error:', error);
      throw error;
    }
  }

  /**
   * Decompose a container into components
   */
  async decomposeContainer(request: DecompositionRequest): Promise<DecompositionResponse> {
    try {
      const response = await apiClient.post<DecompositionResponse>(
        API_ENDPOINTS.DECOMPOSE_CONTAINER,
        request
      );
      return response;
    } catch (error) {
      console.error('Decompose container error:', error);
      throw error;
    }
  }

  /**
   * Suggest API endpoints for a component
   */
  async suggestApiEndpoints(request: APISuggestionRequest): Promise<APISuggestionResponse> {
    try {
      const response = await apiClient.post<APISuggestionResponse>(
        API_ENDPOINTS.SUGGEST_API_ENDPOINTS,
        request
      );
      return response;
    } catch (error) {
      console.error('Suggest API endpoints error:', error);
      throw error;
    }
  }

  /**
   * Get refactoring suggestions for an element
   */
  async refactorElement(request: RefactorRequest): Promise<RefactorResponse> {
    try {
      const response = await apiClient.post<RefactorResponse>(
        API_ENDPOINTS.REFACTOR_ELEMENT,
        request
      );
      return response;
    } catch (error) {
      console.error('Refactor element error:', error);
      throw error;
    }
  }

  /**
   * Get design engine information
   */
  async getEngineInfo(): Promise<EngineInfoResponse> {
    try {
      const response = await apiClient.get<EngineInfoResponse>(
        API_ENDPOINTS.GET_ENGINE_INFO
      );
      return response;
    } catch (error) {
      console.error('Get engine info error:', error);
      throw error;
    }
  }

  /**
   * Get design tree structure
   */
  async getDesignTree(): Promise<DesignTreeResponse> {
    try {
      const response = await apiClient.get<DesignTreeResponse>(
        API_ENDPOINTS.GET_DESIGN_TREE
      );
      return response;
    } catch (error) {
      console.error('Get design tree error:', error);
      throw error;
    }
  }

  /**
   * Execute AI action
   */
  async executeAIAction(request: AIActionRequest): Promise<AIActionResponse> {
    try {
      const response = await apiClient.post<AIActionResponse>(
        API_ENDPOINTS.EXECUTE_AI_ACTION,
        request
      );
      return response;
    } catch (error) {
      console.error('Execute AI action error:', error);
      throw error;
    }
  }

  /**
   * Update design element
   */
  async updateElement(request: ElementUpdateRequest): Promise<ElementUpdateResponse> {
    try {
      const response = await apiClient.put<ElementUpdateResponse>(
        API_ENDPOINTS.UPDATE_ELEMENT,
        request
      );
      return response;
    } catch (error) {
      console.error('Update element error:', error);
      throw error;
    }
  }
}

export const designService = new DesignService();