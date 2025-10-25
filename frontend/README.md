# AI-Powered Software Architecture Generator - Frontend

A React-based frontend application for generating and visualizing software architecture using AI. This application provides an interactive canvas for viewing C4 model diagrams with React Flow, along with an AI chat assistant for architecture discussions.

## Features

- **Interactive Canvas**: Visualize system architecture using React Flow with support for C4 model elements (System Context, Containers, Components)
- **AI Chat Assistant**: Interact with an AI assistant to discuss and refine your architecture
- **Node Details Drawer**: Click on any node to view details and perform actions like technology suggestions, decomposition, and refactoring
- **Modern Tech Stack**: Built with React, TypeScript, Vite, Tailwind CSS, Zustand, and React Flow

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
├── store/              # Zustand state management
│   └── appStore.ts     # Main application store
├── types/              # TypeScript type definitions
│   └── architecture.ts # C4 model types
├── App.tsx             # Main application component
└── main.tsx           # Application entry point
```

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

