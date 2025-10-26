# AI-Powered Software Architecture Generator - Frontend

A React-based frontend application for generating and visualizing software architecture using AI. This application provides an interactive canvas for viewing C4 model diagrams with React Flow, along with an AI chat assistant for architecture discussions.

## Features

- **Interactive Canvas**: Visualize system architecture using React Flow with support for C4 model elements (System Context, Containers, Components)
- **AI Chat Assistant**: Interact with an AI assistant to discuss and refine your architecture
- **Node Details Drawer**: Click on any node to view details and perform actions like technology suggestions, decomposition, and refactoring
- **Backend Integration**: Complete service layer integration with backend APIs for design generation, project management, and AI interactions
- **Modern Tech Stack**: Built with React, TypeScript, Vite, Tailwind CSS, Zustand, and React Flow
- **Authentication**: JWT-based authentication with automatic token management
- **Project Management**: Create, save, and manage architecture projects
- **Real-time AI**: Direct integration with Google Gemini for AI-powered architecture suggestions

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **React Flow** - Canvas and node visualization
- **ESLint** - Code linting

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start dev server
npm run dev
```

The application will be available at `http://localhost:5173/`

### Build

```bash
# Build for production
npm run build
```

### Preview Production Build

```bash
# Preview the production build
npm run preview
```

## Project Structure

```
src/
├── components/          # React components
│   ├── Canvas.tsx       # React Flow canvas
│   ├── ChatPanel.tsx    # AI chat interface
│   └── NodeDrawer.tsx   # Node details drawer
├── services/           # Backend API integration layer
│   ├── apiClient.ts    # Axios client with auth & error handling
│   ├── designService.ts # AI design generation service
│   ├── projectService.ts # Project management service
│   ├── userService.ts   # Authentication & user management
│   ├── geminiService.ts # Direct Gemini AI integration
│   ├── chatService.ts   # Intelligent chat interface
│   ├── healthService.ts # System health monitoring
│   └── config.ts       # API configuration & endpoints
├── store/              # Zustand state management
│   └── appStore.ts     # Main application store
├── types/              # TypeScript type definitions
│   ├── architecture.ts # C4 model types (updated for backend)
│   └── api.ts          # API response & request types
├── App.tsx             # Main application component
└── main.tsx           # Application entry point
```

## Service Layer Integration

The frontend includes a comprehensive service layer that integrates with all backend API endpoints:

### Core Services
- **Design Service**: AI-powered architecture generation, technology suggestions, and component decomposition
- **Project Service**: Complete CRUD operations for architecture projects
- **User Service**: Authentication, user profiles, and session management
- **Chat Service**: Intelligent conversational AI combining multiple AI capabilities
- **Gemini Service**: Direct integration with Google Gemini AI models
- **Health Service**: System health monitoring and diagnostics

### Key Features
- **Automatic Authentication**: JWT token management with automatic refresh
- **Type Safety**: Full TypeScript integration with backend API schemas
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Real-time AI**: Direct access to Google Gemini for various AI tasks
- **Offline Support**: Graceful degradation when backend services are unavailable

For detailed documentation on using the service layer, see [README_SERVICES.md](./README_SERVICES.md).

## Architecture

The application follows the C4 model for software architecture visualization:

- **System Context**: Highest level of abstraction
- **Container**: Deployable units (web servers, databases, etc.)
- **Component**: Logical modules within containers

Each element can have relationships and can be interacted with through the drawer panel for AI-powered actions.

## Available Actions

- **Suggest Technology**: Get AI recommendations for technology choices
- **Decompose into Components**: Break down containers into components
- **Suggest API Endpoints**: Get API endpoint recommendations
- **Refactor Element**: Get refactoring suggestions

## License

This project is part of the System Architect Generator application.

