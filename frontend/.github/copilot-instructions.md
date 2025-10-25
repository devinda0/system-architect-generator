# AI-Powered Software Architecture Generator - Frontend

## Project Overview
This is a React + TypeScript + Vite application for generating and visualizing software architecture using AI. It features an interactive canvas with React Flow for C4 model diagrams and an AI chat assistant.

## Tech Stack
- React 18 with TypeScript
- Vite for building
- Tailwind CSS for styling
- Zustand for state management
- React Flow for canvas visualization
- ESLint for linting

## Architecture
The application follows the C4 model:
- **System Context**: Highest level abstraction
- **Container**: Deployable units (web servers, databases, microservices)
- **Component**: Logical modules within containers

## Development Guidelines
- Use TypeScript strict mode
- Follow React best practices with hooks
- Use Tailwind utility classes for styling
- Manage global state with Zustand
- Keep components focused and reusable

## Project Structure
```
src/
├── components/      # React components (Canvas, ChatPanel, NodeDrawer)
├── store/          # Zustand state management
├── types/          # TypeScript type definitions
└── App.tsx         # Main application component
```

## Available Commands
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Next Steps
- Connect ChatPanel to backend API
- Implement AI-powered actions in NodeDrawer
- Add node creation and editing capabilities
- Implement architecture export/import functionality

