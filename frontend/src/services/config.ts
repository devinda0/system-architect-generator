// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002',
  TIMEOUT: 30000, // 30 seconds
};

export const API_ENDPOINTS = {
  // Health endpoints
  HEALTH: '/api/health',
  
  // Design Engine endpoints
  GENERATE_INITIAL_DESIGN: '/api/designs/generate-initial',
  SUGGEST_TECHNOLOGY: '/api/designs/suggest-technology',
  DECOMPOSE_CONTAINER: '/api/designs/decompose-container',
  SUGGEST_API_ENDPOINTS: '/api/designs/suggest-api',
  REFACTOR_ELEMENT: '/api/designs/refactor',
  GET_ENGINE_INFO: '/api/designs/info',
  GET_DESIGN_TREE: '/api/designs/tree',
  EXECUTE_AI_ACTION: '/api/designs/ai-action',
  UPDATE_ELEMENT: '/api/designs/element',
  
  // Project endpoints
  PROJECTS: '/api/projects',
  PROJECT_BY_ID: (id: string) => `/api/projects/${id}`,
  
  // Gemini endpoints
  GEMINI_HEALTH: '/api/gemini/health',
  GEMINI_GENERATE: '/api/gemini/generate',
  GEMINI_GENERATE_FLASH: '/api/gemini/generate/flash',
  GEMINI_GENERATE_PRO: '/api/gemini/generate/pro',
  GEMINI_BATCH: '/api/gemini/batch',
  
  // User endpoints
  USERS: '/api/users',
  USER_BY_ID: (id: string) => `/api/users/${id}`,
  
  // Authentication endpoints
  AUTH_REGISTER: '/api/auth/register',
  AUTH_LOGIN: '/api/auth/login',
  AUTH_LOGOUT: '/api/auth/logout',
  AUTH_ME: '/api/auth/me',
  AUTH_REFRESH: '/api/auth/refresh',
};
