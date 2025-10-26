# Frontend Service Layer Integration

This document describes the frontend service layer integration with the backend API endpoints for the System Architect Generator.

## Overview

The frontend service layer provides a comprehensive integration with all backend API endpoints, organized into modular services for different domains:

- **Design Service**: AI-powered architecture design generation
- **Project Service**: Project management and persistence
- **User Service**: User authentication and profile management
- **Health Service**: System health monitoring
- **Gemini Service**: Direct AI model interactions
- **Chat Service**: Conversational AI interface

## Service Architecture

### Core Services

#### 1. Design Service (`designService.ts`)
Integrates with the `/api/designs` endpoints for AI-powered architecture generation:

```typescript
// Generate initial system design
const design = await designService.generateInitialDesign("Build a web-based e-commerce platform");

// Suggest technologies for containers
const techSuggestion = await designService.suggestTechnology({
  element_name: "Web Frontend",
  element_type: "container",
  element_description: "React-based user interface",
});

// Decompose containers into components
const decomposition = await designService.decomposeContainer({
  container_name: "API Gateway",
  container_type: "container",
  container_description: "Routes and manages API requests",
});

// Suggest API endpoints for components
const apiSuggestion = await designService.suggestApiEndpoints({
  component_name: "User Service",
  component_type: "component",
  component_description: "Manages user authentication and profiles",
  component_responsibilities: ["authentication", "user management"],
});
```

#### 2. Project Service (`projectService.ts`)
Handles project CRUD operations via `/api/projects`:

```typescript
// Create a new project
const project = await projectService.createProject({
  name: "E-commerce Platform",
  description: "Modern web-based shopping platform",
  tags: ["web", "e-commerce"],
});

// Get user's projects
const projects = await projectService.getProjects(1, 20);

// Update project
const updated = await projectService.updateProject(projectId, {
  description: "Updated description",
});

// Delete project
await projectService.deleteProject(projectId);
```

#### 3. User Service (`userService.ts`)
Manages authentication and user profiles:

```typescript
// Login user
const loginResponse = await userService.login({
  username: "user@example.com",
  password: "password123",
});

// Get current user
const currentUser = userService.getCurrentUser();

// Check authentication status
const isAuthenticated = userService.isAuthenticated();

// Update user profile
const updated = await userService.updateUser(userId, {
  full_name: "John Doe",
  profile: { bio: "Software architect" },
});
```

#### 4. Gemini Service (`geminiService.ts`)
Direct integration with Google Gemini AI models:

```typescript
// Generate architectural suggestions
const suggestions = await geminiService.generateArchitecturalSuggestions(
  "Design a microservices architecture for a social media platform"
);

// Generate code examples
const codeExamples = await geminiService.generateCodeExamples(
  "User Authentication Service",
  "Node.js with Express",
  "JWT-based authentication with password hashing"
);

// Generate API documentation
const apiDocs = await geminiService.generateAPIDocumentation(
  endpoints,
  "User Management Component"
);
```

#### 5. Chat Service (`chatService.ts`)
Intelligent conversational interface combining multiple AI capabilities:

```typescript
// Send a message to AI assistant
const response = await chatService.sendMessage({
  message: "How can I improve the scalability of my web application?",
  context: {
    currentArchitecture: designData,
    selectedNode: containerInfo,
  },
});

// Get conversation history
const history = chatService.getConversationHistory();
```

#### 6. Health Service (`healthService.ts`)
Monitor system health and diagnostics:

```typescript
// Check overall system health
const health = await healthService.checkSystemHealth();

// Perform comprehensive diagnostics
const diagnostics = await healthService.performDiagnostics();

// Monitor health continuously
for await (const healthStatus of healthService.monitorHealth(30000)) {
  console.log('System status:', healthStatus);
}
```

## API Client Configuration

### Base Configuration
The API client is configured in `config.ts`:

```typescript
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  TIMEOUT: 30000,
};
```

### Authentication
The API client automatically handles JWT token authentication:

- Adds `Authorization: Bearer <token>` headers to requests
- Automatically refreshes expired tokens
- Handles authentication errors and token cleanup
- Emits `auth:expired` events for UI handling

### Error Handling
Comprehensive error handling with:

- Custom `ApiError` class with status codes and data
- Automatic retry for token refresh scenarios
- Detailed error logging and context preservation
- User-friendly error messages

## Usage Examples

### Complete Workflow Example

```typescript
import { 
  designService, 
  projectService, 
  chatService,
  userService 
} from '../services';

async function generateArchitecture() {
  try {
    // 1. Generate initial design
    const design = await designService.generateInitialDesign(
      "Build a scalable e-learning platform with video streaming"
    );

    // 2. Get technology suggestions for each container
    for (const container of design.containers) {
      const techSuggestion = await designService.suggestTechnology({
        element_name: container.name,
        element_type: container.type,
        element_description: container.description,
      });
      console.log(`Recommended tech for ${container.name}:`, techSuggestion);
    }

    // 3. Create project with the design
    const project = await projectService.createProject({
      name: design.name,
      description: design.description,
      metadata: { design, generated: true },
    });

    // 4. Start AI conversation about the design
    const chatResponse = await chatService.sendMessage({
      message: "Can you explain the architecture you just generated?",
      context: { 
        currentArchitecture: design,
        projectId: project.id,
      },
    });

    console.log('AI Response:', chatResponse.message);

  } catch (error) {
    console.error('Workflow error:', error);
  }
}
```

### React Component Integration

```typescript
import React, { useState, useEffect } from 'react';
import { designService, projectService } from '../services';
import type { ArchitectureDesign } from '../types/architecture';

function ArchitectureGenerator() {
  const [design, setDesign] = useState<ArchitectureDesign | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async (requirements: string) => {
    setLoading(true);
    try {
      const newDesign = await designService.generateInitialDesign(requirements);
      setDesign(newDesign);
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProject = async () => {
    if (!design) return;
    
    try {
      const project = await projectService.createProject({
        name: design.name,
        description: design.description,
        metadata: { design },
      });
      console.log('Project saved:', project);
    } catch (error) {
      console.error('Save failed:', error);
    }
  };

  return (
    <div>
      {/* Your UI components */}
      <button onClick={() => handleGenerate("Your requirements")}>
        Generate Architecture
      </button>
      {design && (
        <button onClick={handleSaveProject}>
          Save as Project
        </button>
      )}
    </div>
  );
}
```

## Environment Configuration

Set the following environment variables in your `.env` file:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Optional: Enable debug logging
VITE_DEBUG_API=true
```

## Error Handling Patterns

### Service-Level Errors
Each service method includes comprehensive error handling:

```typescript
try {
  const result = await designService.generateInitialDesign(requirements);
  return result;
} catch (error) {
  if (error instanceof ApiError) {
    // Handle API-specific errors
    console.error('API Error:', error.status, error.message);
  } else {
    // Handle network or other errors
    console.error('Unexpected error:', error);
  }
  throw error; // Re-throw for component handling
}
```

### Component-Level Error Handling
Components should handle service errors gracefully:

```typescript
const [error, setError] = useState<string | null>(null);

const handleAction = async () => {
  try {
    setError(null);
    await someService.someMethod();
  } catch (err) {
    setError(err instanceof Error ? err.message : 'An error occurred');
  }
};
```

## Type Safety

All services are fully typed with TypeScript:

- Request/response interfaces match backend schemas
- Proper error type definitions
- Generic type support for flexible usage
- Export of all types for component usage

## Testing

Each service can be tested independently:

```typescript
import { designService } from '../services';

// Mock the API client for testing
jest.mock('../services/apiClient', () => ({
  apiClient: {
    post: jest.fn(),
    get: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  },
}));

describe('DesignService', () => {
  it('should generate initial design', async () => {
    // Test implementation
  });
});
```

## Performance Considerations

- Services implement request caching where appropriate
- Authentication tokens are cached and reused
- Error responses include retry guidance
- Pagination support for large data sets
- Debounced requests for real-time features

## Security Features

- Automatic token management and refresh
- Secure token storage (localStorage with fallback)
- CSRF protection headers
- Request timeout handling
- Input validation and sanitization

This service layer provides a complete, production-ready integration between the frontend UI and backend API, with comprehensive error handling, type safety, and performance optimizations.