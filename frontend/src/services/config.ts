// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  TIMEOUT: 30000, // 30 seconds
};

export const API_ENDPOINTS = {
  // Chat endpoints
  CHAT: '/api/designs/context',
  
  // Architecture endpoints
  GENERATE_INITIAL_DESIGN: '/api/architecture/generate',
  SUGGEST_TECHNOLOGY: '/api/architecture/suggest-technology',
  DECOMPOSE_CONTAINER: '/api/architecture/decompose',
  SUGGEST_API_ENDPOINTS: '/api/architecture/suggest-apis',
  REFACTOR_ELEMENT: '/api/architecture/refactor',
  
  // Project endpoints
  SAVE_PROJECT: '/api/project/save',
  LOAD_PROJECT: '/api/project/load',
  EXPORT_PROJECT: '/api/project/export',
};
