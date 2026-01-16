/**
 * Chat API Service
 *
 * Handles communication with the backend chat API.
 */

import { fetchApi } from './api';

interface ChatRequest {
  message: string;
  conversation_id?: string | null;
}

interface ChatResponse {
  response: string;
  conversation_id: string;
  tool_calls: Array<{
    tool: string;
    status: string;
    result?: string;
  }>;
}

/**
 * Send a message to the chat API
 */
export async function sendMessage(userId: string, message: string, conversationId?: string | null): Promise<ChatResponse> {
  return fetchApi<ChatResponse>(`/api/v1/chat/${userId}`, {
    method: 'POST',
    body: JSON.stringify({
      message,
      conversation_id: conversationId || null
    }),
  });
}

/**
 * Get conversation history
 *
 * Note: Currently the backend doesn't have a dedicated history endpoint,
 * so this would need to be implemented separately if needed.
 */
export async function getConversationHistory(userId: string): Promise<any[]> {
  // Placeholder - implement when backend provides history endpoint
  return [];
}