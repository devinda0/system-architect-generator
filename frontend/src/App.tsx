import { useEffect } from 'react';
import Canvas from './components/Canvas';
import ChatPanel from './components/ChatPanel';
import NodeDrawer from './components/NodeDrawer';
import { useAppStore } from './store/appStore';
import { ElementType } from './types/architecture';

function App() {
  const { setNodes, setEdges } = useAppStore();

  // Initialize with sample data
  useEffect(() => {
    const sampleNodes = [
      {
        id: '1',
        type: 'default',
        position: { x: 250, y: 100 },
        data: {
          label: 'System Context',
          description: 'AI-Powered Software Engineering Workbench',
          element: {
            id: '1',
            name: 'System Context',
            description: 'AI-Powered Software Engineering Workbench',
            type: ElementType.SYSTEM_CONTEXT,
            relationships: [],
          },
        },
      },
      {
        id: '2',
        type: 'default',
        position: { x: 100, y: 250 },
        data: {
          label: 'Frontend Container',
          description: 'React + Vite application',
          technology: 'React + TypeScript',
          element: {
            id: '2',
            name: 'Frontend Container',
            description: 'React + Vite application',
            type: ElementType.CONTAINER,
            technology: 'React + TypeScript',
            relationships: [{ targetId: '3', description: 'Sends API requests to' }],
          },
        },
      },
      {
        id: '3',
        type: 'default',
        position: { x: 400, y: 250 },
        data: {
          label: 'Backend Container',
          description: 'FastAPI server',
          technology: 'FastAPI + Python',
          element: {
            id: '3',
            name: 'Backend Container',
            description: 'FastAPI server',
            type: ElementType.CONTAINER,
            technology: 'FastAPI + Python',
            relationships: [],
          },
        },
      },
    ];

    const sampleEdges = [
      { id: 'e1-2', source: '1', target: '2' },
      { id: 'e1-3', source: '1', target: '3' },
      { id: 'e2-3', source: '2', target: '3', label: 'API calls' },
    ];

    setNodes(sampleNodes);
    setEdges(sampleEdges);
  }, [setNodes, setEdges]);

  return (
    <div className="h-screen w-screen flex overflow-hidden">
      {/* Left side: Canvas with Drawer overlay */}
      <div className="flex-1 relative">
        <Canvas />
        <NodeDrawer />
      </div>

      {/* Right side: Chat Panel */}
      <div className="w-96">
        <ChatPanel />
      </div>
    </div>
  );
}

export default App;
