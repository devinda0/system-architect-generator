import { useState } from 'react';
import { useAppStore } from '../store/appStore';
import { chatService, ApiError } from '../services';
import { renderFromJSON } from '../utils/diagramRenderer';

export default function ChatPanel() {
  const { messages, addMessage, nodes, setNodes,setEdges, currentContext, setCurrentContext, selectedNode } = useAppStore();
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (input.trim()) {
      const userMessage = input.trim();
      addMessage('user', userMessage);
      setInput('');
      setIsLoading(true);

      try {
        // Send message to backend with context
        const response = await chatService.sendMessage({
          query: userMessage,
          currentContext: currentContext || {}
        });

        const {nodes, edges} = renderFromJSON(response as any);
        setNodes(nodes);
        setEdges(edges);
        setCurrentContext(response as any);
      } catch (error) {
        let errorMessage = 'Failed to get response from AI assistant.';
        
        if (error instanceof ApiError) {
          errorMessage = error.message;
        }
        
        addMessage('assistant', `Error: ${errorMessage}`);
        console.error('Chat error:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-50 border-l border-gray-200">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 bg-white">
        <h2 className="text-lg font-semibold text-gray-800">AI Assistant</h2>
        <p className="text-sm text-gray-500">Ask about your architecture</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-400 mt-8">
            <p>Start a conversation with the AI assistant</p>
            <p className="text-sm mt-2">Ask questions about your system architecture</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-200 text-gray-800'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Input */}
      <div className="p-4 bg-white border-t border-gray-200">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={!input.trim() || isLoading}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}
