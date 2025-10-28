import { useState } from 'react';
import { useAppStore } from '../store/appStore';
import type { SystemContext, Container, Component } from '../types/architecture';
import { isSystemContext, isContainer } from '../types/architecture';
import { architectureService, chatService, ApiError } from '../services';
import { renderFromJSON } from '../utils/diagramRenderer';

export default function NodeInfoPanel() {
  const { selectedNode, setSelectedNode, addMessage, currentContext, setCurrentContext, setNodes, setEdges } = useAppStore();
  const [isLoading, setIsLoading] = useState(false);
  const [activeAction, setActiveAction] = useState<string | null>(null);

  if (!selectedNode) {
    return (
      <div className="w-80 bg-gray-50 border-r border-gray-200 flex items-center justify-center">
        <div className="text-center text-gray-400 px-4">
          <svg
            className="w-16 h-16 mx-auto mb-4 text-gray-300"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="text-sm font-medium">No Node Selected</p>
          <p className="text-xs mt-2">Click on a node to view details and actions</p>
        </div>
      </div>
    );
  }

  const nodeData = selectedNode.data as unknown as {
    element: SystemContext | Container | Component;
    label: string;
    technology?: string;
  };

  const element = nodeData.element;
  
  // Count children for display
  const childCount = isSystemContext(element) || isContainer(element) 
    ? element.children.length 
    : 0;

  const handleSuggestTechnology = async () => {
    setIsLoading(true);
    setActiveAction('technology');
    
    try {
      const response = await chatService.sendMessage({
        query: `Suggest suitable technologies for the following element:\n\nName: ${nodeData.label}\nType: ${element.type}\nDescription: ${element.description}`,
        currentContext: currentContext || {}
      })

      const { nodes, edges } = renderFromJSON(response.currentContext as any);
      setNodes(nodes);
      setEdges(edges);
      setCurrentContext(response.currentContext as any);
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : 'Failed to get technology suggestions';
      addMessage('assistant', `Error: ${errorMessage}`);
      console.error('Technology suggestion error:', error);
    } finally {
      setIsLoading(false);
      setActiveAction(null);
    }
  };

  const handleDecompose = async () => {
    setIsLoading(true);
    setActiveAction('decompose');
    
    try {
      const response = await chatService.sendMessage({
        query: `Decompose the following container into its main components:\n\nName: ${nodeData.label}\nDescription: ${element.description}`,
        currentContext: currentContext || {}
      });

      const { nodes, edges } = renderFromJSON(response.currentContext as any);
      setNodes(nodes);
      setEdges(edges);
      setCurrentContext(response.currentContext as any);
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : 'Failed to decompose container';
      addMessage('assistant', `Error: ${errorMessage}`);
      console.error('Decompose error:', error);
    } finally {
      setIsLoading(false);
      setActiveAction(null);
    }
  };

  const handleSuggestApiEndpoints = async () => {
    setIsLoading(true);
    setActiveAction('api');
    
    try {
      const response = await chatService.sendMessage({
        query: `Suggest API endpoints for the following component:\n\nName: ${nodeData.label}\nDescription: ${element.description}`,
        currentContext: currentContext || {}
      });

      const { nodes, edges } = renderFromJSON(response.currentContext as any);
      setNodes(nodes);
      setEdges(edges);
      setCurrentContext(response.currentContext as any);
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : 'Failed to get API suggestions';
      addMessage('assistant', `Error: ${errorMessage}`);
      console.error('API suggestion error:', error);
    } finally {
      setIsLoading(false);
      setActiveAction(null);
    }
  };

  const handleRefactor = async () => {
    setIsLoading(true);
    setActiveAction('refactor');
    
    try {
      const response = await chatService.sendMessage({
        query: `Provide refactoring suggestions for the following element:\n\nName: ${nodeData.label}\nType: ${element.type}\nDescription: ${element.description}`,
        currentContext: currentContext || {}
      });

      const { nodes, edges } = renderFromJSON(response.currentContext as any);
      setNodes(nodes);
      setEdges(edges);
      setCurrentContext(response.currentContext as any);
      
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : 'Failed to get refactoring suggestions';
      addMessage('assistant', `Error: ${errorMessage}`);
      console.error('Refactor error:', error);
    } finally {
      setIsLoading(false);
      setActiveAction(null);
    }
  };

  return (
    <div className="w-80 bg-white border-r border-gray-200 overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b border-gray-200 px-4 py-3 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-800">Node Details</h2>
        {/* <button
          onClick={() => setSelectedNode(null)}
          className="text-gray-500 hover:text-gray-700"
          title="Clear selection"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button> */}
      </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Name
            </label>
            <p className="text-gray-900">{nodeData?.label || selectedNode.id}</p>
          </div>

          {/* Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type
            </label>
            <p className="text-gray-900">{element.type}</p>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <p className="text-gray-900">{element.description}</p>
          </div>

          {/* Technology */}
          {nodeData?.technology && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Technology
              </label>
              <p className="text-gray-900">{nodeData.technology}</p>
            </div>
          )}
          
          {/* Children count */}
          {childCount > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Children
              </label>
              <p className="text-gray-900">
                {childCount} {isSystemContext(element) ? 'container' : 'component'}{childCount !== 1 ? 's' : ''}
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="pt-4 border-t border-gray-200">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Actions
            </label>
            <div className="space-y-2">
              <button
                onClick={handleSuggestTechnology}
                disabled={isLoading}
                className="w-full px-4 py-2 text-sm text-left bg-blue-50 text-blue-700 rounded hover:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {activeAction === 'technology' ? 'Loading...' : 'Suggest Technology'}
              </button>
              <button
                onClick={handleDecompose}
                disabled={isLoading}
                className="w-full px-4 py-2 text-sm text-left bg-green-50 text-green-700 rounded hover:bg-green-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {activeAction === 'decompose' ? 'Loading...' : 'Decompose into Components'}
              </button>
              <button
                onClick={handleSuggestApiEndpoints}
                disabled={isLoading}
                className="w-full px-4 py-2 text-sm text-left bg-purple-50 text-purple-700 rounded hover:bg-purple-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {activeAction === 'api' ? 'Loading...' : 'Suggest API Endpoints'}
              </button>
              <button
                onClick={handleRefactor}
                disabled={isLoading}
                className="w-full px-4 py-2 text-sm text-left bg-amber-50 text-amber-700 rounded hover:bg-amber-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {activeAction === 'refactor' ? 'Loading...' : 'Refactor Element'}
              </button>
            </div>
          </div>

          {/* Relationships */}
          {nodeData?.element?.relationships && nodeData.element.relationships.length > 0 && (
            <div className="pt-4 border-t border-gray-200">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Relationships
              </label>
              <ul className="space-y-2">
                {nodeData.element.relationships.map((rel, index) => (
                  <li key={index} className="text-sm text-gray-600">
                    → {rel.description} ({rel.targetId})
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
  );
}
