import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';

// Project Types based on backend schemas
export interface Project {
  id?: string;
  user_id?: string;
  name: string;
  description?: string;
  tags?: string[];
  status?: 'active' | 'archived' | 'deleted';
  metadata?: Record<string, any>;
  design_count?: number;
  created_at?: string;
  updated_at?: string;
}

export interface ProjectCreateRequest {
  name: string;
  description?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

export interface ProjectUpdateRequest {
  name?: string;
  description?: string;
  tags?: string[];
  status?: 'active' | 'archived';
  metadata?: Record<string, any>;
}

export interface ProjectResponse {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  tags: string[];
  status: string;
  metadata: Record<string, any>;
  design_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectListResponse {
  projects: ProjectResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface ProjectDetailResponse {
  project: ProjectResponse;
  designs: Array<{
    id: string;
    name: string;
    created_at: string;
    updated_at: string;
  }>;
}

class ProjectService {
  /**
   * Create a new project
   */
  async createProject(request: ProjectCreateRequest): Promise<ProjectResponse> {
    try {
      const response = await apiClient.post<ProjectResponse>(
        API_ENDPOINTS.PROJECTS,
        request
      );
      return response;
    } catch (error) {
      console.error('Create project error:', error);
      throw error;
    }
  }

  /**
   * Get list of projects for current user
   */
  async getProjects(
    page: number = 1,
    pageSize: number = 20,
    status?: string,
    tags?: string[]
  ): Promise<ProjectListResponse> {
    try {
      const params: Record<string, any> = {
        page,
        page_size: pageSize,
      };
      
      if (status) params.status = status;
      if (tags && tags.length > 0) params.tags = tags.join(',');

      const response = await apiClient.get<ProjectListResponse>(
        API_ENDPOINTS.PROJECTS,
        params
      );
      return response;
    } catch (error) {
      console.error('Get projects error:', error);
      throw error;
    }
  }

  /**
   * Get project by ID with design details
   */
  async getProjectById(projectId: string): Promise<ProjectDetailResponse> {
    try {
      const response = await apiClient.get<ProjectDetailResponse>(
        API_ENDPOINTS.PROJECT_BY_ID(projectId)
      );
      return response;
    } catch (error) {
      console.error('Get project by ID error:', error);
      throw error;
    }
  }

  /**
   * Update project
   */
  async updateProject(
    projectId: string,
    request: ProjectUpdateRequest
  ): Promise<ProjectResponse> {
    try {
      const response = await apiClient.put<ProjectResponse>(
        API_ENDPOINTS.PROJECT_BY_ID(projectId),
        request
      );
      return response;
    } catch (error) {
      console.error('Update project error:', error);
      throw error;
    }
  }

  /**
   * Delete project
   */
  async deleteProject(projectId: string): Promise<{ message: string }> {
    try {
      const response = await apiClient.delete<{ message: string }>(
        API_ENDPOINTS.PROJECT_BY_ID(projectId)
      );
      return response;
    } catch (error) {
      console.error('Delete project error:', error);
      throw error;
    }
  }

  /**
   * Get project statistics
   */
  async getProjectStats(): Promise<{
    total_projects: number;
    active_projects: number;
    archived_projects: number;
    total_designs: number;
  }> {
    try {
      // This would need to be implemented in the backend
      // For now, derive from the projects list
      const projects = await this.getProjects();
      const stats = {
        total_projects: projects.total,
        active_projects: projects.projects.filter(p => p.status === 'active').length,
        archived_projects: projects.projects.filter(p => p.status === 'archived').length,
        total_designs: projects.projects.reduce((sum, p) => sum + p.design_count, 0),
      };
      return stats;
    } catch (error) {
      console.error('Get project stats error:', error);
      throw error;
    }
  }
}

export const projectService = new ProjectService();
