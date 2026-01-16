'use client';

import { useState, useEffect, useRef } from 'react';
import { useAuthContext } from '@/components/AuthProvider';
import { sendMessage } from '@/services/chatApi';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
}

export default function FloatingChatbot() {
  const { user } = useAuthContext();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Handle opening the chat and initial message
  const handleOpenChat = () => {
    if (!isOpen) {
      setIsOpen(true);
      // Add welcome message if it's the first time opening
      if (messages.length === 0) {
        const welcomeMessage = {
          id: 'welcome',
          content: user
            ? 'Hello! I\'m your AI assistant. How can I help you today?'
            : 'Please sign in to use the AI assistant.',
          role: 'assistant' as const,
          timestamp: new Date().toISOString(),
        };
        setMessages([welcomeMessage]);
      }
    } else {
      setIsOpen(!isOpen);
    }
  };

  // Handle sending messages
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Check if user is authenticated
    if (!user?.id) {
      const userMessage = {
        id: `temp-${Date.now()}`,
        content: inputValue,
        role: 'user' as const,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, userMessage]);
      setInputValue('');

      // Add error message about needing to sign in
      const errorMessage = {
        id: `error-${Date.now()}`,
        content: 'Please sign in to use the AI assistant.',
        role: 'assistant' as const,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
      return;
    }

    // Add user message to UI immediately
    const userMessage = {
      id: `temp-${Date.now()}`,
      content: inputValue,
      role: 'user' as const,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Send to backend API
      const data = await sendMessage(user.id, inputValue);

      // Add assistant response
      const assistantMessage = {
        id: `resp-${Date.now()}`,
        content: data.response,
        role: 'assistant' as const,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: `error-${Date.now()}`,
        content: 'Sorry, I encountered an error. Please try again.',
        role: 'assistant' as const,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Close chat when clicking outside (only when open)
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (isOpen && !(event.target as Element).closest('.floating-chatbot')) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={handleOpenChat}
          className="w-14 h-14 bg-blue-500 text-white rounded-full shadow-lg flex items-center justify-center hover:bg-blue-600 transition-colors"
          aria-label="Open chat"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </button>
      )}

      {/* Chat Container */}
      {isOpen && (
        <div className="floating-chatbot bg-white rounded-lg shadow-xl border border-gray-200 w-80 h-96 flex flex-col max-w-xs sm:max-w-sm">
          {/* Header */}
          <div className="bg-blue-500 text-white p-3 rounded-t-lg flex justify-between items-center">
            <h3 className="font-semibold">AI Assistant</h3>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:text-gray-200 focus:outline-none"
              aria-label="Close chat"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3 bg-gray-50">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] px-3 py-2 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-blue-500 text-white rounded-br-none'
                      : 'bg-gray-200 text-gray-800 rounded-bl-none'
                  }`}
                >
                  <div className="text-sm">{message.content}</div>
                  <div className={`text-xs mt-1 ${message.role === 'user' ? 'text-blue-200' : 'text-gray-500'}`}>
                    {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[80%] px-3 py-2 rounded-lg bg-gray-200 text-gray-800 rounded-bl-none">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <form onSubmit={handleSendMessage} className="border-t border-gray-200 p-2 bg-white">
            <div className="flex gap-1">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 border border-gray-300 rounded-full px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                disabled={isLoading}
              />
              <button
                type="submit"
                className={`px-3 py-2 rounded-full text-white ${
                  isLoading || !inputValue.trim()
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-500 hover:bg-blue-600'
                }`}
                disabled={isLoading || !inputValue.trim()}
                aria-label="Send message"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                </svg>
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}