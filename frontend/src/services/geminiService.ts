import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';

// Gemini Service Types
export interface HealthCheckResponse {
  status: string;
  model_available: boolean;
  api_configured: boolean;
  timestamp: string;
}

export interface GenerateRequest {
  prompt: string;
  max_tokens?: number;
  temperature?: number;
  top_p?: number;
  top_k?: number;
}

export interface GenerateResponse {
  text: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  model: string;
  timestamp: string;
}

export interface BatchGenerateRequest {
  prompts: string[];
  max_tokens?: number;
  temperature?: number;
  top_p?: number;
  top_k?: number;
}

export interface BatchGenerateResponse {
  results: Array<{
    text: string;
    usage?: {
      prompt_tokens: number;
      completion_tokens: number;
      total_tokens: number;
    };
  }>;
  total_usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  model: string;
  timestamp: string;
}

class GeminiService {
  /**
   * Check Gemini API health
   */
  async checkHealth(): Promise<HealthCheckResponse> {
    try {
      const response = await apiClient.get<HealthCheckResponse>(
        API_ENDPOINTS.GEMINI_HEALTH
      );
      return response;
    } catch (error) {
      console.error('Gemini health check error:', error);
      throw error;
    }
  }

  /**
   * Generate text using default Gemini model
   */
  async generate(request: GenerateRequest): Promise<GenerateResponse> {
    try {
      const response = await apiClient.post<GenerateResponse>(
        API_ENDPOINTS.GEMINI_GENERATE,
        request
      );
      return response;
    } catch (error) {
      console.error('Gemini generate error:', error);
      throw error;
    }
  }

  /**
   * Generate text using Gemini Flash (faster, lighter model)
   */
  async generateFlash(request: GenerateRequest): Promise<GenerateResponse> {
    try {
      const response = await apiClient.post<GenerateResponse>(
        API_ENDPOINTS.GEMINI_GENERATE_FLASH,
        request
      );
      return response;
    } catch (error) {
      console.error('Gemini Flash generate error:', error);
      throw error;
    }
  }

  /**
   * Generate text using Gemini Pro (more capable model)
   */
  async generatePro(request: GenerateRequest): Promise<GenerateResponse> {
    try {
      const response = await apiClient.post<GenerateResponse>(
        API_ENDPOINTS.GEMINI_GENERATE_PRO,
        request
      );
      return response;
    } catch (error) {
      console.error('Gemini Pro generate error:', error);
      throw error;
    }
  }

  /**
   * Generate multiple texts in batch
   */
  async batchGenerate(request: BatchGenerateRequest): Promise<BatchGenerateResponse> {
    try {
      const response = await apiClient.post<BatchGenerateResponse>(
        API_ENDPOINTS.GEMINI_BATCH,
        request
      );
      return response;
    } catch (error) {
      console.error('Gemini batch generate error:', error);
      throw error;
    }
  }

  /**
   * Generate architectural suggestions using Gemini
   */
  async generateArchitecturalSuggestions(
    requirements: string,
    context?: any
  ): Promise<GenerateResponse> {
    const prompt = `
    As a senior software architect, analyze the following requirements and provide architectural suggestions:
    
    Requirements: ${requirements}
    ${context ? `Context: ${JSON.stringify(context, null, 2)}` : ''}
    
    Please provide:
    1. High-level architecture recommendations
    2. Technology stack suggestions
    3. Key design patterns to consider
    4. Scalability considerations
    5. Security considerations
    
    Format your response as structured recommendations.
    `;

    return this.generatePro({ 
      prompt, 
      max_tokens: 2000,
      temperature: 0.7 
    });
  }

  /**
   * Generate code examples using Gemini
   */
  async generateCodeExamples(
    component: string,
    technology: string,
    requirements: string
  ): Promise<GenerateResponse> {
    const prompt = `
    Generate code examples for a ${component} component using ${technology}.
    
    Requirements: ${requirements}
    
    Please provide:
    1. Basic implementation structure
    2. Key interfaces/classes
    3. Configuration examples
    4. Error handling patterns
    5. Testing examples
    
    Format the response with clear code blocks and explanations.
    `;

    return this.generatePro({ 
      prompt, 
      max_tokens: 3000,
      temperature: 0.5 
    });
  }

  /**
   * Generate API documentation using Gemini
   */
  async generateAPIDocumentation(
    endpoints: any[],
    component: string
  ): Promise<GenerateResponse> {
    const prompt = `
    Generate comprehensive API documentation for the ${component} component.
    
    Endpoints: ${JSON.stringify(endpoints, null, 2)}
    
    Please provide:
    1. API overview and purpose
    2. Authentication requirements
    3. Request/response formats
    4. Error codes and handling
    5. Usage examples
    6. Rate limiting information
    
    Format as OpenAPI/Swagger documentation.
    `;

    return this.generatePro({ 
      prompt, 
      max_tokens: 4000,
      temperature: 0.3 
    });
  }
}

export const geminiService = new GeminiService();