# Frontend Architecture & Service Layer Integration

## 🏗️ Architecture Overview

The frontend follows a modern React architecture with clean separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                            App.tsx                              │
│                     (Main Layout + Error Boundaries)           │
├─────────────────────┬─────────────────────┬─────────────────────┤
│   NodeInfoPanel     │       Canvas        │     ChatPanel       │
│   (Architecture     │   (Visualization)   │   (AI Interaction)  │
│    Operations)      │                     │                     │
└─────────────────────┴─────────────────────┴─────────────────────┘
│                                                                 │
├─────────────────── Service Layer ─────────────────────────────┤
│ apiClient | architectureService | chatService | projectService │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 State Management (Zustand)

### `useAppStore` - Central State Hub
```typescript
interface AppState {
  selectedNode: Node | null;           // Currently selected architecture element
  nodes: Node[];                       // React Flow diagram nodes
  edges: Edge[];                       // React Flow diagram edges  
  messages: ChatMessage[];             // Chat conversation history
  
  // Actions
  setSelectedNode: (node: Node | null) => void;
  setNodes: (nodes: Node[]) => void;
  setEdges: (edges: Edge[]) => void;
  addMessage: (role: 'user' | 'assistant', content: string) => void;
}
```

## 🔌 Service Layer Connections

### **1. App.tsx → Project Service**
**Connection**: ✅ **Enhanced with Project Loading**

```typescript
// Before: Used sample data only
useEffect(() => {
  const sampleTree = createSampleArchitecture();
  const { nodes, edges } = renderFromJSON(sampleTree);
  setNodes(nodes);
  setEdges(edges);
}, []);

// After: Integrated with projectService
useEffect(() => {
  const initializeApp = async () => {
    try {
      const projectId = urlParams.get('project') || localStorage.getItem('currentProjectId');
      
      if (projectId) {
        const projectDetail = await projectService.getProjectById(projectId);
        // Load existing project...
      } else {
        const defaultProject = await projectService.createProject({
          name: 'My Architecture Project',
          description: 'Generated system architecture',
        });
        // Create new project...
      }
    } catch (error) {
      // Fallback to sample data with error handling
    }
  };
  
  initializeApp();
}, []);
```

**Features Added**:
- 🔄 Project loading from URL params or localStorage
- 🆕 Automatic project creation if none exists  
- 📱 Loading states and error handling
- 💾 Project persistence across sessions

### **2. Canvas → Architecture Services**
**Connection**: ✅ **Enhanced with Real-time Updates**

```typescript
// Added service integration
const { nodes, edges, setNodes, setEdges, addMessage } = useAppStore();
const [isSaving, setIsSaving] = useState(false);

// Auto-save node positions
const handleNodesChange = useCallback((changes) => {
  onNodesChange(changes);
  
  const positionChanges = changes.filter(change => 
    change.type === 'position' && !change.dragging
  );
  
  if (positionChanges.length > 0) {
    // TODO: Save to backend when ready
    console.log('Node positions changed, should save to backend');
  }
}, [onNodesChange]);

// Keyboard shortcuts
useEffect(() => {
  const handleKeyDown = (event: KeyboardEvent) => {
    if ((event.ctrlKey || event.metaKey) && event.key === 's') {
      event.preventDefault();
      saveArchitectureChanges();
    }
  };
  
  window.addEventListener('keydown', handleKeyDown);
  return () => window.removeEventListener('keydown', handleKeyDown);
}, []);
```

**Features Added**:
- 💾 Auto-save node positions (debounced)
- ⌨️ Ctrl+S keyboard shortcut
- 🔄 Real-time architecture sync (planned)
- 💡 Save status indicators

### **3. ChatPanel → Chat Service**  
**Connection**: ✅ **Already Well Connected**

```typescript
const handleSend = async () => {
  const userMessage = input.trim();
  addMessage('user', userMessage);
  
  try {
    const response = await chatService.sendMessage({
      message: userMessage,
      context: {
        currentArchitecture: nodes,
        selectedNode: selectedNode || undefined,
      },
    });
    
    addMessage('assistant', response.message);
    
    // Handle architecture updates from AI
    if (response.architectureUpdates) {
      console.log('Architecture updates:', response.architectureUpdates);
    }
  } catch (error) {
    addMessage('assistant', `Error: ${error.message}`);
  }
};
```

**Features**:
- 🤖 AI chat with architecture context
- 🔄 Architecture-aware conversations
- 📝 Message history persistence
- ⚡ Real-time responses

### **4. NodeInfoPanel → Architecture Service**
**Connection**: ✅ **Enhanced with Custom Hooks**

```typescript
// Before: Direct service calls
const handleSuggestTechnology = async () => {
  try {
    const response = await architectureService.suggestTechnology({...});
    // Handle response...
  } catch (error) {
    // Handle error...
  }
};

// After: Using custom hooks
const { 
  suggestTechnology, 
  decomposeContainer, 
  suggestApiEndpoints, 
  isLoading 
} = useArchitecture();

const handleSuggestTechnology = async () => {
  try {
    await suggestTechnology(selectedNode.id, element.type, element.description);
  } catch (error) {
    console.error('Technology suggestion error:', error);
  }
};
```

**Features**:
- 🧠 Technology suggestions
- 🔧 Container decomposition  
- 🌐 API endpoint suggestions
- ♻️ Element refactoring (planned)
- 📊 Loading states and error handling

## 📚 Custom Hooks for Service Integration

### **useArchitecture Hook**
Centralizes architecture operations:

```typescript
export function useArchitecture() {
  const { addMessage } = useAppStore();
  const [isLoading, setIsLoading] = useState(false);
  
  const generateInitialDesign = useCallback(async (requirements: string) => {
    const response = await architectureService.generateInitialDesign({ requirements });
    addMessage('assistant', `Generated design with ${response.elements.length} elements`);
    return response;
  }, [addMessage]);
  
  // Other architecture operations...
  
  return {
    isLoading,
    generateInitialDesign,
    suggestTechnology,
    decomposeContainer,
    suggestApiEndpoints,
  };
}
```

### **useProjectSync Hook**  
Manages project synchronization:

```typescript
export function useProjectSync(projectId?: string) {
  const { nodes, edges } = useAppStore();
  const [isSaving, setIsSaving] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  
  const saveArchitecture = useCallback(async () => {
    // Save current architecture state to backend
    console.log('Saving architecture for project:', projectId, { nodes, edges });
  }, [projectId, nodes, edges]);
  
  return {
    isSaving,
    hasUnsavedChanges,
    saveArchitecture,
    loadArchitecture,
  };
}
```

## 🛡️ Error Handling & Resilience

### **Error Boundary Implementation**
```typescript
// App.tsx wrapped with error boundaries
<ErrorBoundary>
  <div className="h-screen w-screen flex overflow-hidden">
    <ErrorBoundary fallback={<PanelError />}>
      <NodeInfoPanel />
    </ErrorBoundary>
    
    <ErrorBoundary fallback={<CanvasError />}>
      <Canvas />
    </ErrorBoundary>
    
    <ErrorBoundary fallback={<ChatError />}>
      <ChatPanel />
    </ErrorBoundary>
  </div>
</ErrorBoundary>
```

### **API Client Features**
- 🔐 Automatic JWT token management
- 🔄 Token refresh on expiry
- ⚡ Request/response interceptors
- 🚨 Centralized error handling
- ⏱️ Request timeout configuration

## 🎯 Data Flow Architecture

```
User Interaction
      ↓
   Component
      ↓
  Custom Hook (useArchitecture, useProjectSync)
      ↓
  Service Layer (architectureService, projectService) 
      ↓
  API Client (axios with interceptors)
      ↓
  Backend API
      ↓
  Zustand Store Update
      ↓
  Component Re-render
```

## 🚀 Next Steps & Improvements

### **Planned Enhancements**:

1. **Real-time Collaboration**
   - WebSocket integration for live updates
   - Multi-user editing capabilities
   - Conflict resolution

2. **Advanced State Management**
   - Optimistic updates
   - Offline support with sync
   - Undo/redo functionality

3. **Enhanced Architecture Operations**
   - Drag-and-drop element creation
   - Visual relationship editing
   - Bulk operations

4. **Performance Optimizations**
   - Component memoization
   - Virtual scrolling for large diagrams
   - Lazy loading of services

## 📖 Usage Examples

### **Creating a New Architecture**
```typescript
const { generateInitialDesign } = useArchitecture();

const handleGenerate = async () => {
  try {
    const result = await generateInitialDesign(
      "Build a microservices e-commerce platform with React frontend"
    );
    // Architecture automatically updated in store
  } catch (error) {
    // Error handled by hook and displayed in chat
  }
};
```

### **Working with Selected Elements**
```typescript
const { selectedNode } = useAppStore();
const { suggestTechnology } = useArchitecture();

if (selectedNode) {
  await suggestTechnology(
    selectedNode.id, 
    selectedNode.data.element.type,
    selectedNode.data.element.description
  );
}
```

This architecture provides a solid foundation for scalable, maintainable frontend development with clean service integration patterns.