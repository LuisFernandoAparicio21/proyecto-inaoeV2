import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageSquare,
  Plus,
  Trash2,
  Search,
  Clock,
  ChevronRight,
  FolderOpen,
  Bot
} from 'lucide-react';
import { useState } from 'react';
import type { ChatSession } from '@/types';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

// Modelos disponibles

// Modelos disponibles (fallback si el backend no responde)
const DEFAULT_MODELS = [
  { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash', provider: 'Google' },
  { id: 'gemini-2.0-flash', name: 'Gemini 2.0 Flash', provider: 'Google' },
  { id: 'deepseek-r1:1.5b', name: 'DeepSeek R1', provider: 'Ollama' },
  { id: 'mistral:7b', name: 'Mistral 7B', provider: 'Ollama' },
];

interface SidebarProps {
  sessions: ChatSession[];
  currentSessionId?: string;
  onSelectSession: (sessionId: string) => void;
  onDeleteSession: (sessionId: string) => void;
  onNewChat: () => void;
  isOpen: boolean;
  onClose: () => void;
  selectedModel?: string;
  onModelChange?: (model: string) => void;
}

export function Sidebar({
  sessions,
  currentSessionId,
  onSelectSession,
  onDeleteSession,
  onNewChat,
  isOpen,
  onClose,
  selectedModel = 'gemini-1.5-flash',
  onModelChange,
}: SidebarProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [hoveredSession, setHoveredSession] = useState<string | null>(null);

  const filteredSessions = sessions.filter(session =>
    session.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const groupedSessions = filteredSessions.reduce((groups, session) => {
    const date = new Date(session.updatedAt);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    let group = 'Anterior';
    if (date.toDateString() === today.toDateString()) {
      group = 'Hoy';
    } else if (date.toDateString() === yesterday.toDateString()) {
      group = 'Ayer';
    } else if (today.getTime() - date.getTime() < 7 * 24 * 60 * 60 * 1000) {
      group = 'Esta semana';
    }

    if (!groups[group]) groups[group] = [];
    groups[group].push(session);
    return groups;
  }, {} as Record<string, ChatSession[]>);

  const sidebarContent = (
    <div className="flex flex-col h-full bg-secondary/30">
      {/* INAOE Brand */}
      <div className="p-4 border-b border-border/50">
        <div className="flex items-center gap-3">
          <img
            src="/inaoe-logo.png"
            alt="INAOE"
            className="w-10 h-10 object-contain"
          />
          <div>
            <p className="font-bold text-sm text-primary">INAOE</p>
            <p className="text-[10px] text-muted-foreground">RAG Assistant</p>
          </div>
        </div>
      </div>

      {/* New chat button */}
      <div className="p-4 pb-2">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-primary text-white font-medium shadow-inaoe hover:shadow-inaoe-lg transition-all"
        >
          <Plus className="w-5 h-5" />
          Nueva conversación
        </motion.button>
      </div>

      {/* Model selector */}
      <div className="px-4 pb-2">
        <div className="flex items-center gap-2 mb-1">
          <Bot className="w-3.5 h-3.5 text-muted-foreground" />
          <span className="text-xs text-muted-foreground font-medium">Modelo IA</span>
        </div>
        <Select value={selectedModel} onValueChange={onModelChange}>
          <SelectTrigger className="w-full rounded-xl bg-white border border-border text-sm focus:border-primary/50 focus:ring-2 focus:ring-primary/10">
            <SelectValue placeholder="Seleccionar modelo" />
          </SelectTrigger>
          <SelectContent>
            <div className="px-2 py-1 text-xs text-muted-foreground font-semibold">Google</div>
            {DEFAULT_MODELS.filter(m => m.provider === 'Google').map(model => (
              <SelectItem key={model.id} value={model.id} className="text-sm">
                {model.name}
              </SelectItem>
            ))}
            <div className="px-2 py-1 text-xs text-muted-foreground font-semibold mt-1">Ollama (Local)</div>
            {DEFAULT_MODELS.filter(m => m.provider === 'Ollama').map(model => (
              <SelectItem key={model.id} value={model.id} className="text-sm">
                {model.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Search */}
      <div className="px-4 pb-2">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Buscar conversaciones..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-white border border-border text-sm placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/10 transition-all"
          />
        </div>
      </div>

      {/* Sessions list */}
      <div className="flex-1 overflow-y-auto px-2 py-2 scrollbar-thin">
        {Object.entries(groupedSessions).map(([group, groupSessions]) => (
          <div key={group} className="mb-4">
            <h3 className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              {group}
            </h3>
            <div className="space-y-1">
              {groupSessions.map((session) => (
                <motion.div
                  key={session.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  onHoverStart={() => setHoveredSession(session.id)}
                  onHoverEnd={() => setHoveredSession(null)}
                  className={`
                    relative group flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer
                    transition-all duration-200
                    ${currentSessionId === session.id
                      ? 'bg-primary/10 border border-primary/30'
                      : 'hover:bg-white border border-transparent hover:border-border/50'
                    }
                  `}
                  onClick={() => {
                    onSelectSession(session.id);
                    onClose();
                  }}
                >
                  <MessageSquare className={`
                    w-4 h-4 flex-shrink-0
                    ${currentSessionId === session.id ? 'text-primary' : 'text-muted-foreground'}
                  `} />

                  <div className="flex-1 min-w-0">
                    <p className={`
                      text-sm truncate
                      ${currentSessionId === session.id ? 'text-foreground font-medium' : 'text-muted-foreground'}
                    `}>
                      {session.title}
                    </p>
                    <p className="text-[10px] text-muted-foreground/60 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(session.updatedAt).toLocaleTimeString('es-ES', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>

                  {/* Delete button */}
                  <AnimatePresence>
                    {hoveredSession === session.id && (
                      <motion.button
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8 }}
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteSession(session.id);
                        }}
                        className="p-1.5 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-all"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </motion.button>
                    )}
                  </AnimatePresence>

                  {currentSessionId === session.id && (
                    <ChevronRight className="w-4 h-4 text-primary" />
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        ))}

        {filteredSessions.length === 0 && (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <FolderOpen className="w-10 h-10 text-muted-foreground/30 mb-2" />
            <p className="text-sm text-muted-foreground">
              {searchQuery ? 'No se encontraron conversaciones' : 'No hay conversaciones'}
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-border/50 bg-white/50">
        <div className="flex items-center gap-3 px-3 py-2 rounded-xl bg-secondary/50">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
            <span className="text-xs font-medium text-white">U</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">Usuario</p>
            <p className="text-[10px] text-muted-foreground">Investigador</p>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex flex-col w-72 h-full border-r border-border/50 bg-white">
        {sidebarContent}
      </aside>

      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={onClose}
              className="lg:hidden fixed inset-0 z-40 bg-black/20 backdrop-blur-sm"
            />
            <motion.aside
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="lg:hidden fixed left-0 top-0 z-50 w-72 h-full bg-white border-r border-border/50"
            >
              {sidebarContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
