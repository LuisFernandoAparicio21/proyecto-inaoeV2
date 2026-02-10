import { useState, useCallback, useRef } from 'react';
import type { Message, ChatSession, Source } from '@/types';

const generateId = () => Math.random().toString(36).substring(2, 9);

// URL del backend - configurar según el entorno
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const createWelcomeMessage = (): Message => ({
  id: generateId(),
  role: 'assistant',
  content: '¡Hola! Soy tu asistente de investigación del INAOE. Puedo ayudarte a encontrar información en los documentos científicos y responder preguntas basándome en la base de conocimiento institucional. ¿En qué puedo ayudarte hoy?',
  timestamp: new Date(),
});

export function useChat(selectedModel: string = 'gemini-1.5-flash') {
  const [sessions, setSessions] = useState<ChatSession[]>([
    {
      id: '1',
      title: 'Bienvenida',
      messages: [createWelcomeMessage()],
      createdAt: new Date(),
      updatedAt: new Date(),
    },
  ]);
  const [currentSessionId, setCurrentSessionId] = useState<string>('1');
  const [isLoading, setIsLoading] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const currentSession = sessions.find(s => s.id === currentSessionId);

  const createNewSession = useCallback(() => {
    const newSession: ChatSession = {
      id: generateId(),
      title: 'Nueva conversación',
      messages: [createWelcomeMessage()],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    setSessions(prev => [newSession, ...prev]);
    setCurrentSessionId(newSession.id);
    return newSession.id;
  }, []);

  const selectSession = useCallback((sessionId: string) => {
    setCurrentSessionId(sessionId);
  }, []);

  const deleteSession = useCallback((sessionId: string) => {
    setSessions(prev => {
      const filtered = prev.filter(s => s.id !== sessionId);
      if (filtered.length === 0) {
        const newSession: ChatSession = {
          id: generateId(),
          title: 'Nueva conversación',
          messages: [createWelcomeMessage()],
          createdAt: new Date(),
          updatedAt: new Date(),
        };
        setCurrentSessionId(newSession.id);
        return [newSession];
      }
      if (currentSessionId === sessionId) {
        setCurrentSessionId(filtered[0].id);
      }
      return filtered;
    });
  }, [currentSessionId]);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;

    // Create new abort controller for this request
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    const assistantMessage: Message = {
      id: generateId(),
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
    };

    // Add user message and placeholder for assistant
    setSessions(prev => prev.map(session => {
      if (session.id === currentSessionId) {
        const updatedMessages = [...session.messages, userMessage, assistantMessage];
        return {
          ...session,
          messages: updatedMessages,
          title: session.messages.length === 1 ? content.slice(0, 30) + (content.length > 30 ? '...' : '') : session.title,
          updatedAt: new Date(),
        };
      }
      return session;
    }));

    setIsLoading(true);

    try {
      // Llamar al backend FastAPI
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pregunta: content.trim(),
          modelo: selectedModel,
          num_docs: 5,
          temperature: 0.2,
          timeout: 120,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      // Convert backend sources to frontend Source format
      const sources: Source[] = data.fuentes.map((f: { source: string; page: number | string }, idx: number) => ({
        id: String(idx + 1),
        title: f.source,
        content: '',
        relevance: 1.0 - (idx * 0.1),
        metadata: {
          page: typeof f.page === 'number' ? f.page : parseInt(f.page) || 0,
        },
      }));

      // Update with the actual response
      setSessions(prev => prev.map(session => {
        if (session.id === currentSessionId) {
          return {
            ...session,
            messages: session.messages.map(msg =>
              msg.id === assistantMessage.id
                ? { ...msg, content: data.respuesta, isStreaming: false, sources }
                : msg
            ),
            updatedAt: new Date(),
          };
        }
        return session;
      }));

    } catch (error) {
      // Error handling
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido';

      setSessions(prev => prev.map(session => {
        if (session.id === currentSessionId) {
          return {
            ...session,
            messages: session.messages.map(msg =>
              msg.id === assistantMessage.id
                ? {
                  ...msg,
                  content: `❌ Error al consultar el backend: ${errorMessage}\n\nAsegúrate de que el servidor esté corriendo en ${API_BASE_URL}`,
                  isStreaming: false
                }
                : msg
            ),
            updatedAt: new Date(),
          };
        }
        return session;
      }));
    }

    setIsLoading(false);
  }, [currentSessionId, isLoading, selectedModel]);

  const regenerateResponse = useCallback(async (messageId: string) => {
    // Find the corresponding user message and resend
    const session = sessions.find(s => s.id === currentSessionId);
    if (!session) return;

    const messageIndex = session.messages.findIndex(m => m.id === messageId);
    if (messageIndex <= 0) return;

    const userMessage = session.messages[messageIndex - 1];
    if (userMessage && userMessage.role === 'user') {
      // Remove the current assistant message
      setSessions(prev => prev.map(s => {
        if (s.id === currentSessionId) {
          return {
            ...s,
            messages: s.messages.filter(m => m.id !== messageId),
          };
        }
        return s;
      }));
      // Resend the user message
      await sendMessage(userMessage.content);
    }
  }, [currentSessionId, sessions, sendMessage]);

  return {
    sessions,
    currentSession,
    currentSessionId,
    isLoading,
    createNewSession,
    selectSession,
    deleteSession,
    sendMessage,
    regenerateResponse,
  };
}
