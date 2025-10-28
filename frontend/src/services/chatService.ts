import type { SystemContext } from '../types/architecture';
import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  currentContext: SystemContext | {};
  query: string;
}

export interface ChatResponse {
  currentContext: SystemContext | {};
}

class ChatService {
  /**
   * Send a chat message to the AI assistant
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await apiClient.post<ChatResponse>(
        API_ENDPOINTS.CHAT,
        request
      );
      console.log('Chat service response:', response);
      return response;
    } catch (error) {
      console.error('Chat service error:', error);
      throw error;
    }
  }
}

export const chatService = new ChatService();
