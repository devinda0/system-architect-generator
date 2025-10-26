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
    <div className="h-full w-full">
      <ReactFlow
        nodes={localNodes}
        edges={localEdges}
        onNodesChange={onNodesChange}
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
