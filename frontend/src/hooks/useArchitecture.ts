import { useState, useCallback } from 'react';
import { useAppStore } from '../store/appStore';
import { architectureService, ApiError } from '../services';

/**
 * Custom hook for managing architecture operations
 */
export function useArchitecture() {
  const { setNodes, setEdges, addMessage } = useAppStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateInitialDesign = useCallback(async (requirements: string, projectName?: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await architectureService.generateInitialDesign({
        requirements,
        projectName,
      });

      // Convert response to architecture tree and render
      // TODO: Convert API response to SystemContext format when backend is ready
      addMessage('assistant', `Generated initial design with ${response.elements.length} elements and ${response.relationships.length} relationships.`);
      
      return response;
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : 'Failed to generate design';
      setError(errorMessage);
      addMessage('assistant', `Error: ${errorMessage}`);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [setNodes, setEdges, addMessage]);

  const suggestTechnology = useCallback(async (elementId: string, elementType: string, context?: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await architectureService.suggestTechnology({
        elementId,
        elementType,
        context,
      });

      const suggestions = response.suggestions
        .map(s => `**${s.technology}**\n${s.reasoning}\n\nPros: ${s.pros.join(', ')}\nCons: ${s.cons.join(', ')}`)
        .join('\n\n');

      addMessage('assistant', `Technology suggestions:\n\n${suggestions}`);
      return response;
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : 'Failed to get technology suggestions';
      setError(errorMessage);
      addMessage('assistant', `Error: ${errorMessage}`);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [addMessage]);

  const decomposeContainer = useCallback(async (containerId: string, containerName: string, technology?: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await architectureService.decomposeContainer({
        containerId,
        containerName,
        technology,
      });

      // TODO: Update canvas with new components when backend response format is ready
      addMessage('assistant', `Decomposed ${containerName} into ${response.components.length} components.`);
      return response;
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : 'Failed to decompose container';
      setError(errorMessage);
      addMessage('assistant', `Error: ${errorMessage}`);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [addMessage]);

  const suggestApiEndpoints = useCallback(async (componentId: string, componentName: string, description?: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await architectureService.suggestApiEndpoints({
        componentId,
        componentName,
        description,
      });

      const endpoints = response.endpoints
        .map(e => `${e.method.toUpperCase()} ${e.path} - ${e.description}`)
        .join('\n');

      addMessage('assistant', `API suggestions for ${componentName}:\n\n${endpoints}`);
      return response;
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : 'Failed to get API suggestions';
      setError(errorMessage);
      addMessage('assistant', `Error: ${errorMessage}`);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [addMessage]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // State
    isLoading,
    error,
    
    // Actions
    generateInitialDesign,
    suggestTechnology,
    decomposeContainer,
    suggestApiEndpoints,
    clearError,
  };
}

/**
 * Custom hook for design operations
 */
export function useDesignOperations() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const executeAIAction = useCallback(async (actionType: string, targetElement?: string, parameters?: any, context?: any) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // TODO: Implement when design service AI action endpoint is ready
      console.log('Executing AI action:', { actionType, targetElement, parameters, context });
      
      // Placeholder response
      return { result: 'Action executed successfully' };
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : 'Failed to execute AI action';
      setError(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refactorElement = useCallback(async (elementId: string, elementType: string, refactoringGoal: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await architectureService.refactorElement({
        elementId,
        elementType,
        refactoringGoal,
      });

      return response;
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : 'Failed to refactor element';
      setError(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isLoading,
    error,
    executeAIAction,
    refactorElement,
  };
}

/**
 * Custom hook for project synchronization
 */
export function useProjectSync(projectId?: string) {
  const { nodes, edges } = useAppStore();
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const saveArchitecture = useCallback(async () => {
    if (!projectId || isSaving) return;
    
    setIsSaving(true);
    try {
      // TODO: Implement save to project when backend supports architecture storage
      console.log('Saving architecture for project:', projectId, { nodes, edges });
      
      setLastSaved(new Date());
      setHasUnsavedChanges(false);
    } catch (error) {
      console.error('Failed to save architecture:', error);
      throw error;
    } finally {
      setIsSaving(false);
    }
  }, [projectId, nodes, edges, isSaving]);

  const loadArchitecture = useCallback(async () => {
    if (!projectId) return;
    
    try {
      // TODO: Load architecture from project when backend supports it
      console.log('Loading architecture for project:', projectId);
    } catch (error) {
      console.error('Failed to load architecture:', error);
      throw error;
    }
  }, [projectId]);

  // Auto-save functionality (could be debounced)
  const markAsChanged = useCallback(() => {
    setHasUnsavedChanges(true);
  }, []);

  return {
    lastSaved,
    isSaving,
    hasUnsavedChanges,
    saveArchitecture,
    loadArchitecture,
    markAsChanged,
  };
}