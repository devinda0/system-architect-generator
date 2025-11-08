import { useState } from 'react';
import { useAppStore } from '../store/appStore';
import { chatService, ApiError } from '../services';
import { renderFromJSON } from '../utils/diagramRenderer';

export default function ChatPanel() {
  const { messages, addMessage, setNodes, setEdges, currentContext, setCurrentContext } = useAppStore();
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
    <div className="h-full flex flex-col bg-gradient-to-b from-slate-50 to-white border-l-2 border-gray-200/50 shadow-xl">
      {/* Header */}
      <div className="px-6 py-4 border-b-2 border-blue-400 bg-gradient-to-r from-blue-600 to-indigo-600 shadow-lg">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-2.5 h-2.5 rounded-full bg-green-400 animate-pulse shadow-lg shadow-green-400/50" />
          <h2 className="text-xl font-bold text-white drop-shadow-md">AI Assistant</h2>
        </div>
        <p className="text-sm text-blue-100 font-medium">Ask about your architecture</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-slate-50/50 to-white">
        {messages.length === 0 ? (
          <div className="text-center mt-12 space-y-4">
            <div className="w-16 h-16 mx-auto bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-xl">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <p className="text-gray-600 font-medium">Start a conversation with AI</p>
            <p className="text-sm text-gray-400">Ask questions about your system architecture</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 shadow-md transition-all duration-300 hover:shadow-lg ${
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-blue-600 to-indigo-600 text-white'
                    : 'bg-white border-2 border-gray-200 text-gray-800'
                }`}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Input */}
      <div className="p-4 bg-white border-t-2 border-gray-200/50 shadow-2xl">
        <div className="flex gap-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 bg-gray-50 hover:bg-white disabled:opacity-50"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            className={`px-6 py-3 rounded-xl font-semibold shadow-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
              !input.trim() || isLoading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700 hover:shadow-xl hover:scale-105'
            }`}
            disabled={!input.trim() || isLoading}
          >
            {isLoading ? (
              <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            ) : (
              'Send'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
