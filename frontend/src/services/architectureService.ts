import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';
import type { ArchitectureElement } from '../types/architecture';

export interface GenerateDesignRequest {
  requirements: string;
  projectName?: string;
}

export interface GenerateDesignResponse {
  elements: ArchitectureElement[];
  relationships: Array<{
    sourceId: string;
    targetId: string;
    description: string;
  }>;
}

export interface SuggestTechnologyRequest {
  elementId: string;
  elementType: string;
  context?: string;
}

export interface SuggestTechnologyResponse {
  suggestions: Array<{
    technology: string;
    reasoning: string;
    pros: string[];
    cons: string[];
  }>;
}

export interface DecomposeContainerRequest {
  containerId: string;
  containerName: string;
  technology?: string;
}

export interface DecomposeContainerResponse {
  components: ArchitectureElement[];
  relationships: Array<{
    sourceId: string;
    targetId: string;
    description: string;
  }>;
}

export interface SuggestApiEndpointsRequest {
  componentId: string;
  componentName: string;
  description?: string;
}

export interface SuggestApiEndpointsResponse {
  endpoints: Array<{
    method: string;
    path: string;
    description: string;
    requestBody?: any;
    responseBody?: any;
  }>;
}

export interface RefactorElementRequest {
  elementId: string;
  elementType: string;
  refactoringGoal: string;
}

export interface RefactorElementResponse {
  suggestions: string[];
  updatedElement?: ArchitectureElement;
  additionalElements?: ArchitectureElement[];
}

class ArchitectureService {
  /**
   * Generate initial architecture design from requirements
   */
  async generateInitialDesign(
    request: GenerateDesignRequest
  ): Promise<GenerateDesignResponse> {
    try {
      const response = await apiClient.post<GenerateDesignResponse>(
        API_ENDPOINTS.GENERATE_INITIAL_DESIGN,
        request
      );
      return response;
    } catch (error) {
      console.error('Generate design error:', error);
      throw error;
    }
  }

  /**
   * Get technology suggestions for an element
   */
  async suggestTechnology(
    request: SuggestTechnologyRequest
  ): Promise<SuggestTechnologyResponse> {
    try {
      const response = await apiClient.post<SuggestTechnologyResponse>(
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
  async decomposeContainer(
    request: DecomposeContainerRequest
  ): Promise<DecomposeContainerResponse> {
    try {
      const response = await apiClient.post<DecomposeContainerResponse>(
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
  async suggestApiEndpoints(
    request: SuggestApiEndpointsRequest
  ): Promise<SuggestApiEndpointsResponse> {
    try {
      const response = await apiClient.post<SuggestApiEndpointsResponse>(
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
  async refactorElement(
    request: RefactorElementRequest
  ): Promise<RefactorElementResponse> {
    try {
      const response = await apiClient.post<RefactorElementResponse>(
        API_ENDPOINTS.REFACTOR_ELEMENT,
        request
      );
      return response;
    } catch (error) {
      console.error('Refactor element error:', error);
      throw error;
    }
  }
}

export const architectureService = new ArchitectureService();
