import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  context?: {
    currentArchitecture?: any;
    selectedNode?: any;
  };
}

export interface ChatResponse {
  message: string;
  suggestions?: string[];
  architectureUpdates?: any;
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
      return response;
    } catch (error) {
      console.error('Chat service error:', error);
      throw error;
    }
  }

  /**
   * Send a streaming chat message (for future implementation)
   */
  async *streamMessage(request: ChatRequest): AsyncGenerator<string> {
    // TODO: Implement streaming chat using Server-Sent Events or WebSocket
    // For now, fall back to regular message
    const response = await this.sendMessage(request);
    yield response.message;
  }
}

export const chatService = new ChatService();
