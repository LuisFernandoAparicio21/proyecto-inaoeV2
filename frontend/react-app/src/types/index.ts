export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];
  isStreaming?: boolean;
}

export interface Source {
  id: string;
  title: string;
  content: string;
  relevance: number;
  metadata?: {
    page?: number;
    author?: string;
    date?: string;
    url?: string;
  };
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Suggestion {
  id: string;
  text: string;
  category: string;
}
