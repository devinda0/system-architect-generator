import { useCallback, useMemo, useEffect, useState } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  type OnConnect,
  type Node,
  type NodeTypes,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useAppStore } from '../store/appStore';
import SystemContextNode from './nodes/SystemContextNode';
import ContainerNode from './nodes/ContainerNode';
import ComponentNode from './nodes/ComponentNode';

export default function Canvas() {
  const { nodes, edges, setEdges, setSelectedNode, addMessage } = useAppStore();
  const [isSaving, setIsSaving] = useState(false);
  
  const [localNodes, setLocalNodes, onNodesChange] = useNodesState(nodes);
  const [localEdges, setLocalEdges, onEdgesChange] = useEdgesState(edges);

  // Sync local state with store when store updates
  useEffect(() => {
    setLocalNodes(nodes);
  }, [nodes, setLocalNodes]);

  useEffect(() => {
    setLocalEdges(edges);
  }, [edges, setLocalEdges]);

  // Define custom node types
  const nodeTypes: NodeTypes = useMemo(
    () => ({
      systemContext: SystemContextNode,
      container: ContainerNode,
      component: ComponentNode,
    }),
    []
  );

  // Auto-save node positions when they change
  const handleNodesChange = useCallback(
    (changes: any[]) => {
      onNodesChange(changes);
      
      // Debounce save operation for position changes
      const positionChanges = changes.filter(change => change.type === 'position' && !change.dragging);
      if (positionChanges.length > 0) {
        // TODO: Implement auto-save to backend
        console.log('Node positions changed, should save to backend');
      }
    },
    [onNodesChange]
  );

  // Save architecture changes to backend
  const saveArchitectureChanges = useCallback(async () => {
    if (isSaving) return;
    
    setIsSaving(true);
    try {
      // TODO: Implement save to backend when design storage is ready
      // await designService.updateDesign(currentProjectId, { nodes: localNodes, edges: localEdges });
      console.log('Architecture saved successfully');
    } catch (error) {
      console.error('Failed to save architecture:', error);
      addMessage('assistant', 'Failed to save architecture changes. Please try again.');
    } finally {
      setIsSaving(false);
    }
  }, [isSaving, localNodes, localEdges, addMessage]);

  const onConnect: OnConnect = useCallback(
    (params) => {
      const newEdges = addEdge(params, localEdges);
      setLocalEdges(newEdges);
      setEdges(newEdges);
      
      // Auto-save when connections are made
      // saveArchitectureChanges();
    },
    [localEdges, setLocalEdges, setEdges]
  );

  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      setSelectedNode(node);
    },
    [setSelectedNode]
  );

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ctrl/Cmd + S to save
      if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault();
        saveArchitectureChanges();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [saveArchitectureChanges]);

  return (
    <div className="h-full w-full relative">
      {/* Save Status Indicator */}
      {isSaving && (
        <div className="absolute top-4 right-4 z-10 bg-blue-100 border border-blue-200 rounded-lg px-3 py-2 flex items-center space-x-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          <span className="text-blue-700 text-sm">Saving...</span>
        </div>
      )}

      {/* Keyboard Shortcuts Helper */}
      <div className="absolute bottom-4 left-4 z-10 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-75">
        Ctrl+S to save
      </div>

      <ReactFlow
        nodes={localNodes}
        edges={localEdges}
        onNodesChange={handleNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.1}
        maxZoom={2}
      >
        <Background />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            if (node.type === 'systemContext') return '#3b82f6';
            if (node.type === 'container') return '#10b981';
            if (node.type === 'component') return '#8b5cf6';
            return '#6b7280';
          }}
        />
      </ReactFlow>
    </div>
  );
}
