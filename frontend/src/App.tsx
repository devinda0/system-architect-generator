import { useEffect } from 'react';
import Canvas from './components/Canvas';
import ChatPanel from './components/ChatPanel';
import NodeInfoPanel from './components/NodeInfoPanel';
import { useAppStore } from './store/appStore';
import { createSampleArchitecture } from './utils/architectureConverter';
import { renderFromJSON } from './utils/diagramRenderer';

function App() {
  const { setNodes, setEdges } = useAppStore();

  // Initialize with sample architecture tree
  useEffect(() => {
    const sampleTree = createSampleArchitecture();
    
    // Convert tree to React Flow nodes and edges
    const { nodes, edges } = renderFromJSON(sampleTree);
    setNodes(nodes);
    setEdges(edges);
  }, []);

  return (
    <div className="h-screen w-screen flex overflow-hidden bg-gradient-to-br from-slate-100 via-blue-50 to-indigo-100">
      {/* Left side: Node Details Panel */}
      <NodeInfoPanel />

      {/* Middle: Canvas */}
      <div className="flex-1 relative shadow-inner">
        <Canvas />
      </div>

      {/* Right side: Chat Panel */}
      <div className="w-96">
        <ChatPanel />
      </div>
    </div>
  );
}

export default App;
