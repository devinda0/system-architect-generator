import { useEffect, useState } from 'react';
import Canvas from './components/Canvas';
import ChatPanel from './components/ChatPanel';
import NodeInfoPanel from './components/NodeInfoPanel';
import ErrorBoundary from './components/ErrorBoundary';
import AuthTest from './components/AuthTest';
import { AuthWrapper } from './components/AuthWrapper';
import { Header } from './components/Header';
import { useAppStore } from './store/appStore';
import { createSampleArchitecture } from './utils/architectureConverter';
import { renderSystemContextDiagram } from './utils/diagramRenderer';
import { projectService, ApiError } from './services';
import { AuthProvider, useAuth } from './contexts/AuthContext';

function AppContent() {
  const { setNodes, setEdges, addMessage } = useAppStore();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAuthTest, setShowAuthTest] = useState(false);
  const [currentProjectId, setCurrentProjectId] = useState<string | null>(null);

  // Initialize with project data or fallback to sample
  useEffect(() => {
    // Only initialize if authenticated
    if (!isAuthenticated) {
      return;
    }

    const initializeApp = async () => {
      setLoading(true);
      setError(null);

      try {
        // Try to get the current project from URL params or localStorage
        const urlParams = new URLSearchParams(window.location.search);
        const projectId = urlParams.get('project') || localStorage.getItem('currentProjectId');

        if (projectId) {
          // Load existing project
          const projectDetail = await projectService.getProjectById(projectId);
          const project = projectDetail.project;
          setCurrentProjectId(project.id);
          localStorage.setItem('currentProjectId', project.id);

          // For now, initialize with sample data since project architecture structure needs to be defined
          // TODO: When project.architecture is available, use it instead
          initializeSampleData();
          addMessage('assistant', `Loaded project: ${project.name}. ${project.description || 'Start by describing your system requirements.'}`);
        } else {
          // Create a new default project or use sample data
          const defaultProject = await projectService.createProject({
            name: 'My Architecture Project',
            description: 'Generated system architecture',
          });
          
          setCurrentProjectId(defaultProject.id);
          localStorage.setItem('currentProjectId', defaultProject.id);
          initializeSampleData();
          addMessage('assistant', `Created new project: ${defaultProject.name}. You can start by describing your system requirements or exploring the sample architecture.`);
        }
      } catch (error) {
        console.error('Failed to initialize project:', error);
        setError(error instanceof ApiError ? error.message : 'Failed to load project');
        
        // Fallback to sample data
        initializeSampleData();
        addMessage('assistant', 'Using sample architecture. Connect to the backend to save your work.');
      } finally {
        setLoading(false);
      }
    };

    const initializeSampleData = () => {
      const sampleTree = createSampleArchitecture();
      const { nodes, edges } = renderSystemContextDiagram(sampleTree);
      setNodes(nodes);
      setEdges(edges);
    };

    initializeApp();
  }, [isAuthenticated, setNodes, setEdges, addMessage]);

  // Show authentication screen if not authenticated
  if (authLoading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Loading...</h2>
          <p className="text-gray-500">Checking authentication status...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthWrapper onAuthSuccess={() => {}} />;
  }

  // Loading state
  if (loading) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Loading Project</h2>
          <p className="text-gray-500">Setting up your architecture workspace...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md">
          <div className="text-red-500 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.854-.833-2.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-700 mb-2">Failed to Load Project</h2>
          <p className="text-gray-500 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Show AuthTest if toggled
  if (showAuthTest) {
    return (
      <div className="h-screen w-screen">
        <div className="absolute top-4 right-4 z-50">
          <button
            onClick={() => setShowAuthTest(false)}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            Back to App
          </button>
        </div>
        <AuthTest />
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="h-screen w-screen flex flex-col overflow-hidden">
        {/* Header with user info and logout */}
        <Header />
        
        <div className="flex-1 flex overflow-hidden">
          {/* Project Header - now as a banner below the main header */}
          {currentProjectId && (
            <div className="absolute top-16 left-0 right-0 bg-blue-50 border-b border-blue-200 px-4 py-2 z-10">
              <div className="flex items-center justify-between">
                <div className="text-sm text-blue-800">
                  Project: <span className="font-medium">My Architecture Project</span>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-xs text-blue-600">
                    ID: {currentProjectId.slice(0, 8)}...
                  </div>
                  <button
                    onClick={() => setShowAuthTest(true)}
                    className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700"
                  >
                    Test Auth
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Left side: Node Details Panel */}
          <ErrorBoundary fallback={
            <div className="w-80 bg-gray-50 border-r border-gray-200 flex items-center justify-center">
              <p className="text-gray-500 text-sm">Error loading panel</p>
            </div>
          }>
            <NodeInfoPanel />
          </ErrorBoundary>

          {/* Middle: Canvas */}
          <div className="flex-1 relative" style={{ marginTop: currentProjectId ? '50px' : '0' }}>
            <ErrorBoundary fallback={
              <div className="h-full flex items-center justify-center bg-gray-50">
                <p className="text-gray-500">Error loading canvas</p>
              </div>
            }>
              <Canvas />
            </ErrorBoundary>
          </div>

          {/* Right side: Chat Panel */}
          <div className="w-96 border-l border-gray-200" style={{ marginTop: currentProjectId ? '50px' : '0' }}>
            <ErrorBoundary fallback={
              <div className="h-full flex items-center justify-center bg-gray-50">
                <p className="text-gray-500 text-sm">Error loading chat</p>
              </div>
            }>
              <ChatPanel />
            </ErrorBoundary>
          </div>

          {/* Floating Auth Test Button (when no project header) */}
          {!currentProjectId && (
            <button
              onClick={() => setShowAuthTest(true)}
              className="absolute top-4 right-4 z-50 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow-lg"
            >
              Test Auth
            </button>
          )}
        </div>
      </div>
    </ErrorBoundary>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
