import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';
import type { ArchitectureElement } from '../types/architecture';

export interface Project {
  id?: string;
  name: string;
  description?: string;
  elements: ArchitectureElement[];
  createdAt?: string;
  updatedAt?: string;
}

export interface SaveProjectRequest {
  project: Project;
}

export interface SaveProjectResponse {
  projectId: string;
  message: string;
}

export interface LoadProjectRequest {
  projectId: string;
}

export interface LoadProjectResponse {
  project: Project;
}

export interface ExportProjectRequest {
  projectId: string;
  format: 'json' | 'yaml' | 'diagram';
}

export interface ExportProjectResponse {
  content: string;
  filename: string;
}

class ProjectService {
  /**
   * Save project to backend
   */
  async saveProject(request: SaveProjectRequest): Promise<SaveProjectResponse> {
    try {
      const response = await apiClient.post<SaveProjectResponse>(
        API_ENDPOINTS.SAVE_PROJECT,
        request
      );
      return response;
    } catch (error) {
      console.error('Save project error:', error);
      throw error;
    }
  }

  /**
   * Load project from backend
   */
  async loadProject(request: LoadProjectRequest): Promise<LoadProjectResponse> {
    try {
      const response = await apiClient.get<LoadProjectResponse>(
        `${API_ENDPOINTS.LOAD_PROJECT}/${request.projectId}`
      );
      return response;
    } catch (error) {
      console.error('Load project error:', error);
      throw error;
    }
  }

  /**
   * Export project in various formats
   */
  async exportProject(
    request: ExportProjectRequest
  ): Promise<ExportProjectResponse> {
    try {
      const response = await apiClient.post<ExportProjectResponse>(
        API_ENDPOINTS.EXPORT_PROJECT,
        request
      );
      return response;
    } catch (error) {
      console.error('Export project error:', error);
      throw error;
    }
  }
}

export const projectService = new ProjectService();
