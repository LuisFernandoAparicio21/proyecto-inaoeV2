import { motion } from 'framer-motion';
import { Settings, History, Plus, Menu, X } from 'lucide-react';

interface ChatHeaderProps {
  onNewChat?: () => void;
  onToggleSidebar?: () => void;
  isSidebarOpen?: boolean;
  title?: string;
}

export function ChatHeader({
  onNewChat,
  onToggleSidebar,
  isSidebarOpen = false,
  title = 'Nueva conversación'
}: ChatHeaderProps) {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="sticky top-0 z-50 w-full bg-white/90 backdrop-blur-md border-b border-border/60"
    >
      <div className="flex items-center justify-between h-16 px-4">
        {/* Left section */}
        <div className="flex items-center gap-3">
          {/* Mobile menu toggle */}
          <button
            onClick={onToggleSidebar}
            className="lg:hidden p-2 rounded-lg text-muted-foreground hover:text-primary hover:bg-secondary transition-all"
          >
            {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Center - Title */}
        <div className="flex-1 flex justify-center px-4">
          <motion.h2
            key={title}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-sm font-medium text-foreground truncate max-w-xs"
          >
            {title}
          </motion.h2>
        </div>

        {/* Right section */}
        <div className="flex items-center gap-1">
          {/* New chat button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onNewChat}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm text-muted-foreground hover:text-primary hover:bg-secondary transition-all"
          >
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Nuevo chat</span>
          </motion.button>

          {/* History button */}
          <button
            className="p-2 rounded-lg text-muted-foreground hover:text-primary hover:bg-secondary transition-all"
            title="Historial"
          >
            <History className="w-4 h-4" />
          </button>

          {/* Settings button */}
          <button
            className="p-2 rounded-lg text-muted-foreground hover:text-primary hover:bg-secondary transition-all"
            title="Configuración"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>
    </motion.header>
  );
}
