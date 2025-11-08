import { useState } from 'react';
import { useAppStore } from '../store/appStore';
import type { SystemContext, Container, Component } from '../types/architecture';
import { isSystemContext, isContainer } from '../types/architecture';
import { chatService, ApiError } from '../services';
import { renderFromJSON } from '../utils/diagramRenderer';

export default function NodeInfoPanel() {
  const { selectedNode, addMessage, currentContext, setCurrentContext, setNodes, setEdges } = useAppStore();
  const [isLoading, setIsLoading] = useState(false);
  const [activeAction, setActiveAction] = useState<string | null>(null);

  if (!selectedNode) {
    return (
      <div className="w-80 bg-gradient-to-b from-slate-50 to-white border-r-2 border-gray-200/50 shadow-xl flex items-center justify-center">
        <div className="text-center px-6 space-y-4">
          <div className="w-20 h-20 mx-auto bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-2xl">
            <svg
              className="w-10 h-10 text-white"
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
          </div>
          <p className="text-base font-bold text-gray-700">No Node Selected</p>
          <p className="text-sm text-gray-500 leading-relaxed">Click on a node to view details and actions</p>
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

      const { nodes, edges } = renderFromJSON(response as any);
      setNodes(nodes);
      setEdges(edges);
      setCurrentContext(response as any);
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

      const { nodes, edges } = renderFromJSON(response as any);
      setNodes(nodes);
      setEdges(edges);
      setCurrentContext(response as any);
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

      const { nodes, edges } = renderFromJSON(response as any);
      setNodes(nodes);
      setEdges(edges);
      setCurrentContext(response as any);
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

      const { nodes, edges } = renderFromJSON(response as any);
      setNodes(nodes);
      setEdges(edges);
      setCurrentContext(response as any);
      
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
    <div className="w-80 bg-gradient-to-b from-slate-50 to-white border-r-2 border-gray-200/50 shadow-xl overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-indigo-600 border-b-2 border-blue-400 px-6 py-4 flex justify-between items-center shadow-lg z-10">
        <div>
          <h2 className="text-xl font-bold text-white drop-shadow-md">Node Details</h2>
          <p className="text-xs text-blue-100 mt-0.5">Selected Element</p>
        </div>
      </div>

        {/* Content */}
        <div className="p-6 space-y-5">
          {/* Name */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-200 shadow-sm">
            <label className="block text-xs font-bold text-blue-700 uppercase tracking-wider mb-2">
              Name
            </label>
            <p className="text-gray-900 font-semibold text-lg">{nodeData?.label || selectedNode.id}</p>
          </div>

          {/* Type */}
          <div className="bg-white rounded-xl p-4 border-2 border-gray-200 shadow-sm">
            <label className="block text-xs font-bold text-gray-600 uppercase tracking-wider mb-2">
              Type
            </label>
            <p className="text-gray-900 font-medium">{element.type}</p>
          </div>

          {/* Description */}
          <div className="bg-white rounded-xl p-4 border-2 border-gray-200 shadow-sm">
            <label className="block text-xs font-bold text-gray-600 uppercase tracking-wider mb-2">
              Description
            </label>
            <p className="text-gray-700 leading-relaxed">{element.description}</p>
          </div>

          {/* Technology */}
          {nodeData?.technology && (
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4 border border-purple-200 shadow-sm">
              <label className="block text-xs font-bold text-purple-700 uppercase tracking-wider mb-2">
                Technology
              </label>
              <p className="text-gray-900 font-medium">{nodeData.technology}</p>
            </div>
          )}
          
          {/* Children count */}
          {childCount > 0 && (
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-4 border border-green-200 shadow-sm">
              <label className="block text-xs font-bold text-green-700 uppercase tracking-wider mb-2">
                Children
              </label>
              <p className="text-gray-900 font-medium">
                {childCount} {isSystemContext(element) ? 'container' : 'component'}{childCount !== 1 ? 's' : ''}
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="pt-2">
            <label className="block text-xs font-bold text-gray-600 uppercase tracking-wider mb-3">
              Quick Actions
            </label>
            <div className="space-y-3">
              <button
                onClick={handleSuggestTechnology}
                disabled={isLoading}
                className="w-full px-4 py-3 text-sm font-semibold text-left bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl hover:from-blue-600 hover:to-blue-700 shadow-md hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-md flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                {activeAction === 'technology' ? 'Loading...' : 'Suggest Technology'}
              </button>
              <button
                onClick={handleDecompose}
                disabled={isLoading}
                className="w-full px-4 py-3 text-sm font-semibold text-left bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl hover:from-green-600 hover:to-emerald-700 shadow-md hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-md flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1v-3z" />
                </svg>
                {activeAction === 'decompose' ? 'Loading...' : 'Decompose'}
              </button>
              <button
                onClick={handleSuggestApiEndpoints}
                disabled={isLoading}
                className="w-full px-4 py-3 text-sm font-semibold text-left bg-gradient-to-r from-purple-500 to-violet-600 text-white rounded-xl hover:from-purple-600 hover:to-violet-700 shadow-md hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-md flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {activeAction === 'api' ? 'Loading...' : 'API Endpoints'}
              </button>
              <button
                onClick={handleRefactor}
                disabled={isLoading}
                className="w-full px-4 py-3 text-sm font-semibold text-left bg-gradient-to-r from-amber-500 to-orange-600 text-white rounded-xl hover:from-amber-600 hover:to-orange-700 shadow-md hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-md flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                {activeAction === 'refactor' ? 'Loading...' : 'Refactor'}
              </button>
            </div>
          </div>

          {/* Relationships */}
          {nodeData?.element?.relationships && nodeData.element.relationships.length > 0 && (
            <div className="pt-2">
              <label className="block text-xs font-bold text-gray-600 uppercase tracking-wider mb-3">
                Relationships
              </label>
              <ul className="space-y-2">
                {nodeData.element.relationships.map((rel, index) => (
                  <li key={index} className="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg p-3 text-sm text-gray-700 border border-indigo-200 shadow-sm">
                    <span className="text-indigo-600 font-semibold">→</span> {rel.description}
                    <span className="block text-xs text-gray-500 mt-1">{rel.targetId}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
  );
}
