import { geminiService } from './geminiService';
import { designService } from './designService';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  metadata?: {
    type?: 'text' | 'code' | 'architecture' | 'suggestion';
    actions?: Array<{
      label: string;
      action: string;
      data?: any;
    }>;
  };
}

export interface ChatRequest {
  message: string;
  context?: {
    currentArchitecture?: any;
    selectedNode?: any;
    projectId?: string;
    conversationHistory?: ChatMessage[];
  };
}

export interface ChatResponse {
  message: string;
  suggestions?: string[];
  architectureUpdates?: any;
  actions?: Array<{
    label: string;
    action: string;
    data?: any;
  }>;
  metadata?: {
    type: 'text' | 'code' | 'architecture' | 'suggestion';
    confidence?: number;
    sources?: string[];
  };
}

class ChatService {
  private conversationHistory: ChatMessage[] = [];

  /**
   * Send a chat message to the AI assistant
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      // Add user message to history
      const userMessage: ChatMessage = {
        role: 'user',
        content: request.message,
        timestamp: new Date().toISOString(),
      };
      
      if (request.context?.conversationHistory) {
        this.conversationHistory = request.context.conversationHistory;
      }
      this.conversationHistory.push(userMessage);

      // Determine the type of request and route accordingly
      const messageType = this.categorizeMessage(request.message);
      
      let response: ChatResponse;
      
      switch (messageType) {
        case 'architecture_generation':
          response = await this.handleArchitectureGeneration(request);
          break;
        case 'technology_suggestion':
          response = await this.handleTechnologySuggestion(request);
          break;
        case 'code_generation':
          response = await this.handleCodeGeneration(request);
          break;
        case 'general_question':
        default:
          response = await this.handleGeneralQuestion(request);
          break;
      }

      // Add assistant response to history
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
        metadata: response.metadata,
      };
      this.conversationHistory.push(assistantMessage);

      return response;
    } catch (error) {
      console.error('Chat service error:', error);
      throw error;
    }
  }

  /**
   * Handle architecture generation requests
   */
  private async handleArchitectureGeneration(request: ChatRequest): Promise<ChatResponse> {
    try {
      // Extract requirements from the message
      const requirements = this.extractRequirements(request.message);
      
      if (requirements) {
        const designResponse = await designService.generateInitialDesign(requirements);
        
        return {
          message: this.formatArchitectureResponse(designResponse),
          architectureUpdates: designResponse,
          actions: [
            {
              label: 'Apply Architecture',
              action: 'apply_architecture',
              data: designResponse,
            },
            {
              label: 'Suggest Technologies',
              action: 'suggest_technologies',
              data: { containers: designResponse.containers },
            },
          ],
          metadata: {
            type: 'architecture',
            confidence: 0.9,
          },
        };
      } else {
        // Use Gemini for architectural suggestions
        const geminiResponse = await geminiService.generateArchitecturalSuggestions(
          request.message,
          request.context
        );
        
        return {
          message: geminiResponse.text,
          suggestions: this.extractSuggestions(geminiResponse.text),
          metadata: {
            type: 'suggestion',
            confidence: 0.7,
          },
        };
      }
    } catch (error) {
      console.error('Architecture generation error:', error);
      throw error;
    }
  }

  /**
   * Handle technology suggestion requests
   */
  private async handleTechnologySuggestion(request: ChatRequest): Promise<ChatResponse> {
    try {
      const context = request.context;
      if (context?.selectedNode) {
        const techResponse = await designService.suggestTechnology({
          element_name: context.selectedNode.name,
          element_type: context.selectedNode.type,
          element_description: context.selectedNode.description,
          element_context: context.currentArchitecture,
        });

        return {
          message: this.formatTechnologyResponse(techResponse),
          suggestions: [
            techResponse.primary_recommendation.technology,
            ...techResponse.alternatives.map(alt => alt.technology),
          ],
          actions: [
            {
              label: 'Apply Technology',
              action: 'apply_technology',
              data: techResponse.primary_recommendation,
            },
          ],
          metadata: {
            type: 'suggestion',
            confidence: 0.85,
          },
        };
      } else {
        // Generic technology discussion
        const geminiResponse = await geminiService.generate({
          prompt: `As a technology expert, answer this question: ${request.message}`,
          temperature: 0.7,
        });

        return {
          message: geminiResponse.text,
          metadata: {
            type: 'text',
            confidence: 0.8,
          },
        };
      }
    } catch (error) {
      console.error('Technology suggestion error:', error);
      throw error;
    }
  }

  /**
   * Handle code generation requests
   */
  private async handleCodeGeneration(request: ChatRequest): Promise<ChatResponse> {
    try {
      const context = request.context;
      const selectedNode = context?.selectedNode;
      
      if (selectedNode) {
        const geminiResponse = await geminiService.generateCodeExamples(
          selectedNode.name,
          selectedNode.technology || 'generic',
          request.message
        );

        return {
          message: geminiResponse.text,
          actions: [
            {
              label: 'Generate API Docs',
              action: 'generate_api_docs',
              data: { component: selectedNode.name },
            },
          ],
          metadata: {
            type: 'code',
            confidence: 0.8,
          },
        };
      } else {
        const geminiResponse = await geminiService.generate({
          prompt: `As a senior developer, help with this coding question: ${request.message}`,
          temperature: 0.5,
        });

        return {
          message: geminiResponse.text,
          metadata: {
            type: 'code',
            confidence: 0.7,
          },
        };
      }
    } catch (error) {
      console.error('Code generation error:', error);
      throw error;
    }
  }

  /**
   * Handle general questions
   */
  private async handleGeneralQuestion(request: ChatRequest): Promise<ChatResponse> {
    try {
      const contextualPrompt = this.buildContextualPrompt(request);
      
      const geminiResponse = await geminiService.generate({
        prompt: contextualPrompt,
        temperature: 0.7,
      });

      return {
        message: geminiResponse.text,
        suggestions: this.extractSuggestions(geminiResponse.text),
        metadata: {
          type: 'text',
          confidence: 0.75,
        },
      };
    } catch (error) {
      console.error('General question error:', error);
      throw error;
    }
  }

  /**
   * Categorize the type of message
   */
  private categorizeMessage(message: string): string {
    const lower = message.toLowerCase();
    
    if (lower.includes('generate') && (lower.includes('architecture') || lower.includes('system') || lower.includes('design'))) {
      return 'architecture_generation';
    }
    
    if (lower.includes('technology') || lower.includes('tech stack') || lower.includes('framework') || lower.includes('library')) {
      return 'technology_suggestion';
    }
    
    if (lower.includes('code') || lower.includes('implement') || lower.includes('example') || lower.includes('api')) {
      return 'code_generation';
    }
    
    return 'general_question';
  }

  /**
   * Extract requirements from user message
   */
  private extractRequirements(message: string): string | null {
    // Simple heuristic - if the message is long enough and contains architectural terms
    if (message.length > 50 && (
      message.toLowerCase().includes('system') ||
      message.toLowerCase().includes('application') ||
      message.toLowerCase().includes('service') ||
      message.toLowerCase().includes('platform')
    )) {
      return message;
    }
    return null;
  }

  /**
   * Format architecture response
   */
  private formatArchitectureResponse(response: any): string {
    return `I've generated an initial architecture for your system:

**System Overview:**
${response.system_context.description}

**Containers:**
${response.containers.map((container: any) => 
  `- **${container.name}**: ${container.description} (${container.technology})`
).join('\n')}

**Key Design Decisions:**
${response.design_rationale.key_decisions.map((decision: any) => 
  `- ${decision.decision}: ${decision.rationale}`
).join('\n')}

Would you like me to elaborate on any specific component or suggest technologies for the containers?`;
  }

  /**
   * Format technology response
   */
  private formatTechnologyResponse(response: any): string {
    return `For ${response.element_name}, I recommend:

**Primary Recommendation: ${response.primary_recommendation.technology}**
${response.primary_recommendation.rationale}

**Pros:**
${response.primary_recommendation.pros_cons.pros.map((pro: string) => `- ${pro}`).join('\n')}

**Cons:**
${response.primary_recommendation.pros_cons.cons.map((con: string) => `- ${con}`).join('\n')}

**Alternative Options:**
${response.alternatives.map((alt: any) => `- ${alt.technology}: ${alt.rationale}`).join('\n')}

**Integration Considerations:**
${response.integration_considerations.map((consideration: string) => `- ${consideration}`).join('\n')}`;
  }

  /**
   * Extract suggestions from text
   */
  private extractSuggestions(text: string): string[] {
    // Simple extraction - look for bullet points or numbered lists
    const suggestions = [];
    const lines = text.split('\n');
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.match(/^[-*•]\s+/) || trimmed.match(/^\d+\.\s+/)) {
        suggestions.push(trimmed.replace(/^[-*•]\s+/, '').replace(/^\d+\.\s+/, ''));
      }
    }
    
    return suggestions.slice(0, 5); // Limit to 5 suggestions
  }

  /**
   * Build contextual prompt with conversation history
   */
  private buildContextualPrompt(request: ChatRequest): string {
    let prompt = `You are an expert software architect and developer assistant. `;
    
    if (request.context?.currentArchitecture) {
      prompt += `The user is working on a system with the following architecture: ${JSON.stringify(request.context.currentArchitecture, null, 2)}\n\n`;
    }
    
    if (this.conversationHistory.length > 1) {
      prompt += `Previous conversation context:\n`;
      const recentHistory = this.conversationHistory.slice(-4); // Last 4 messages
      for (const msg of recentHistory) {
        prompt += `${msg.role}: ${msg.content}\n`;
      }
      prompt += `\n`;
    }
    
    prompt += `Current question: ${request.message}`;
    
    return prompt;
  }

  /**
   * Get conversation history
   */
  getConversationHistory(): ChatMessage[] {
    return [...this.conversationHistory];
  }

  /**
   * Clear conversation history
   */
  clearHistory(): void {
    this.conversationHistory = [];
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
