import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';

export interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'degraded';
  timestamp: string;
  version?: string;
  uptime?: number;
}

export interface SystemHealthResponse {
  api: HealthStatus;
  database: HealthStatus;
  gemini: HealthStatus;
  overall: HealthStatus;
  services: {
    [key: string]: HealthStatus;
  };
}

class HealthService {
  /**
   * Check overall system health
   */
  async checkSystemHealth(): Promise<SystemHealthResponse> {
    try {
      const response = await apiClient.get<SystemHealthResponse>(
        API_ENDPOINTS.HEALTH
      );
      return response;
    } catch (error) {
      console.error('System health check error:', error);
      throw error;
    }
  }

  /**
   * Check API health
   */
  async checkAPIHealth(): Promise<HealthStatus> {
    try {
      const response = await apiClient.get<HealthStatus>(
        API_ENDPOINTS.HEALTH
      );
      return response;
    } catch (error) {
      console.error('API health check error:', error);
      return {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
      };
    }
  }

  /**
   * Perform comprehensive system diagnostics
   */
  async performDiagnostics(): Promise<{
    api: boolean;
    gemini: boolean;
    database: boolean;
    overall: boolean;
    errors: string[];
  }> {
    const diagnostics = {
      api: false,
      gemini: false,
      database: false,
      overall: false,
      errors: [] as string[],
    };

    try {
      // Check API health
      const apiHealth = await this.checkAPIHealth();
      diagnostics.api = apiHealth.status === 'healthy';
      if (!diagnostics.api) {
        diagnostics.errors.push('API is not healthy');
      }
    } catch (error) {
      diagnostics.errors.push(`API check failed: ${error}`);
    }

    try {
      // Check Gemini health
      const { geminiService } = await import('./geminiService');
      const geminiHealth = await geminiService.checkHealth();
      diagnostics.gemini = geminiHealth.status === 'healthy';
      if (!diagnostics.gemini) {
        diagnostics.errors.push('Gemini service is not healthy');
      }
    } catch (error) {
      diagnostics.errors.push(`Gemini check failed: ${error}`);
    }

    // Overall health is true if API is healthy (minimum requirement)
    diagnostics.overall = diagnostics.api;

    return diagnostics;
  }

  /**
   * Monitor system health continuously
   */
  async *monitorHealth(intervalMs: number = 30000): AsyncGenerator<SystemHealthResponse> {
    while (true) {
      try {
        const health = await this.checkSystemHealth();
        yield health;
      } catch (error) {
        console.error('Health monitoring error:', error);
        yield {
          api: { status: 'unhealthy', timestamp: new Date().toISOString() },
          database: { status: 'unhealthy', timestamp: new Date().toISOString() },
          gemini: { status: 'unhealthy', timestamp: new Date().toISOString() },
          overall: { status: 'unhealthy', timestamp: new Date().toISOString() },
          services: {},
        };
      }
      
      // Wait for the specified interval
      await new Promise(resolve => setTimeout(resolve, intervalMs));
    }
  }
}

export const healthService = new HealthService();