import { useCallback, useMemo, useEffect } from 'react';
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
  const { nodes, edges, setEdges, setSelectedNode } = useAppStore();
  
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

  const onConnect: OnConnect = useCallback(
    (params) => {
      const newEdges = addEdge(params, localEdges);
      setLocalEdges(newEdges);
      setEdges(newEdges);
    },
    [localEdges, setLocalEdges, setEdges]
  );

  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      setSelectedNode(node);
    },
    [setSelectedNode]
  );

  return (
    <div className="h-full w-full bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/30">
      <ReactFlow
        nodes={localNodes}
        edges={localEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{
          padding: 0.3,
          maxZoom: 1,
        }}
        minZoom={0.1}
        maxZoom={1.5}
        defaultEdgeOptions={{
          type: 'smoothstep',
          animated: true,
          style: { strokeWidth: 2.5 },
        }}
      >
        <Background 
          gap={20}
          size={1.5}
          color="#e0e7ff"
          className="bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/30"
        />
        <Controls 
          className="bg-white/90 backdrop-blur-sm border border-gray-200 rounded-lg shadow-lg"
          showInteractive={false}
        />
        <MiniMap
          className="bg-white/90 backdrop-blur-sm border-2 border-gray-200 rounded-lg shadow-lg"
          nodeColor={(node) => {
            if (node.type === 'systemContext') return '#6366f1';
            if (node.type === 'container') return '#f97316';
            if (node.type === 'component') return '#a855f7';
            return '#6b7280';
          }}
          maskColor="rgba(0, 0, 0, 0.05)"
          nodeStrokeWidth={3}
        />
      </ReactFlow>
    </div>
  );
}
