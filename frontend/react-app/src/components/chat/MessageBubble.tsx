import { motion } from 'framer-motion';
import { User, Bot, Copy, Check, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';
import type { Message } from '@/types';
import { TypingIndicator } from '@/components/ui-custom/TypingIndicator';
import { SourceCard } from './SourceCard';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const [showSources, setShowSources] = useState(true);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isUser = message.role === 'user';
  const hasSources = message.sources && message.sources.length > 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.1, duration: 0.3 }}
        className={`
          flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center
          ${isUser 
            ? 'bg-gradient-to-br from-primary to-primary/80 shadow-inaoe' 
            : 'bg-secondary border border-border'
          }
        `}
      >
        {isUser ? (
          <User className="w-5 h-5 text-primary-foreground" />
        ) : (
          <Bot className="w-5 h-5 text-primary" />
        )}
      </motion.div>

      {/* Message content */}
      <div className={`flex-1 max-w-[85%] ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-2`}>
        {/* Bubble */}
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.15, duration: 0.3 }}
          className={`
            relative group px-5 py-4 rounded-2xl
            ${isUser 
              ? 'message-bubble-user rounded-tr-sm' 
              : 'message-bubble-ai rounded-tl-sm'
            }
          `}
        >
          {/* Copy button */}
          <button
            onClick={handleCopy}
            className={`
              absolute top-2 right-2 p-1.5 rounded-lg opacity-0 group-hover:opacity-100
              transition-all duration-200
              ${isUser ? 'text-white/70 hover:text-white hover:bg-white/10' : 'text-muted-foreground hover:text-primary hover:bg-secondary'}
            `}
            title="Copiar mensaje"
          >
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
          </button>

          {/* Content */}
          {message.isStreaming && !message.content ? (
            <TypingIndicator />
          ) : (
            <div className={`
              prose prose-sm max-w-none
              ${isUser ? 'prose-invert' : 'prose-slate'}
            `}>
              <div className="markdown-content whitespace-pre-wrap">
                {message.content}
                {message.isStreaming && (
                  <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse" />
                )}
              </div>
            </div>
          )}
        </motion.div>

        {/* Sources section */}
        {hasSources && !isUser && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            transition={{ delay: 0.3, duration: 0.3 }}
            className="w-full mt-2"
          >
            <button
              onClick={() => setShowSources(!showSources)}
              className="flex items-center gap-2 text-xs text-muted-foreground hover:text-primary transition-colors mb-2"
            >
              <span className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                Fuentes relevantes ({message.sources!.length})
              </span>
              {showSources ? (
                <ChevronUp className="w-3.5 h-3.5" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5" />
              )}
            </button>
            
            {showSources && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="grid gap-2"
              >
                {message.sources!.map((source, index) => (
                  <SourceCard 
                    key={source.id} 
                    source={source} 
                    index={index}
                  />
                ))}
              </motion.div>
            )}
          </motion.div>
        )}

        {/* Timestamp */}
        <span className="text-[10px] text-muted-foreground px-1">
          {message.timestamp.toLocaleTimeString('es-ES', { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </span>
      </div>
    </motion.div>
  );
}
