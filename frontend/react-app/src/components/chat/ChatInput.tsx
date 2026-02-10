import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Paperclip, Mic, Sparkles, X } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
}

export function ChatInput({ 
  onSend, 
  isLoading = false,
  placeholder = 'Escribe tu mensaje...'
}: ChatInputProps) {
  const [input, setInput] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input.trim());
      setInput('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const quickSuggestions = [
    'Explica este documento',
    'Resume los puntos clave',
    'Encuentra información sobre...',
  ];

  return (
    <div className="w-full">
      {/* Quick suggestions */}
      <AnimatePresence>
        {isFocused && input === '' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="flex gap-2 mb-3 overflow-x-auto pb-2 scrollbar-thin"
          >
            {quickSuggestions.map((suggestion, index) => (
              <motion.button
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.05 }}
                onClick={() => setInput(suggestion)}
                className="flex-shrink-0 px-3 py-1.5 text-xs bg-secondary hover:bg-secondary/80 border border-border hover:border-primary/30 rounded-full text-muted-foreground hover:text-primary transition-all whitespace-nowrap"
              >
                <Sparkles className="w-3 h-3 inline mr-1.5 text-primary" />
                {suggestion}
              </motion.button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input container */}
      <motion.div
        initial={false}
        animate={{
          boxShadow: isFocused 
            ? '0 0 0 2px hsl(220 85% 28% / 0.2), 0 4px 12px hsl(220 85% 28% / 0.1)' 
            : '0 0 0 0px transparent',
        }}
        className={`
          relative flex items-end gap-2 p-3 rounded-2xl
          bg-white border border-border
          transition-all duration-300
          ${isFocused ? 'border-primary/50' : 'hover:border-border/80'}
        `}
      >
        {/* Attachment button */}
        <button
          type="button"
          className="flex-shrink-0 p-2 rounded-xl text-muted-foreground hover:text-primary hover:bg-secondary transition-all"
          title="Adjuntar archivo"
        >
          <Paperclip className="w-5 h-5" />
        </button>

        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          disabled={isLoading}
          rows={1}
          className={`
            flex-1 min-h-[44px] max-h-[200px] py-2.5 px-2
            bg-transparent text-sm text-foreground placeholder:text-muted-foreground
            resize-none outline-none
            disabled:opacity-50 disabled:cursor-not-allowed
          `}
        />

        {/* Clear button */}
        <AnimatePresence>
          {input && (
            <motion.button
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              onClick={() => setInput('')}
              className="flex-shrink-0 p-1.5 rounded-lg text-muted-foreground hover:text-primary hover:bg-secondary transition-all"
            >
              <X className="w-4 h-4" />
            </motion.button>
          )}
        </AnimatePresence>

        {/* Voice button */}
        <button
          type="button"
          className="flex-shrink-0 p-2 rounded-xl text-muted-foreground hover:text-primary hover:bg-secondary transition-all"
          title="Entrada de voz"
        >
          <Mic className="w-5 h-5" />
        </button>

        {/* Send button */}
        <motion.button
          type="button"
          onClick={() => handleSubmit()}
          disabled={!input.trim() || isLoading}
          whileHover={{ scale: input.trim() && !isLoading ? 1.05 : 1 }}
          whileTap={{ scale: input.trim() && !isLoading ? 0.95 : 1 }}
          className={`
            flex-shrink-0 p-3 rounded-xl
            transition-all duration-300
            ${input.trim() && !isLoading
              ? 'bg-gradient-to-r from-primary to-primary/90 text-white shadow-inaoe hover:shadow-inaoe-lg'
              : 'bg-secondary text-muted-foreground cursor-not-allowed'
            }
          `}
        >
          {isLoading ? (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            >
              <Sparkles className="w-5 h-5" />
            </motion.div>
          ) : (
            <Send className="w-5 h-5" />
          )}
        </motion.button>
      </motion.div>

      {/* Footer hint */}
      <div className="flex justify-between items-center mt-2 px-1">
        <span className="text-[10px] text-muted-foreground">
          Presiona <kbd className="px-1.5 py-0.5 rounded bg-secondary text-[10px] border border-border">Enter</kbd> para enviar,{' '}
          <kbd className="px-1.5 py-0.5 rounded bg-secondary text-[10px] border border-border">Shift + Enter</kbd> para nueva línea
        </span>
        <span className="text-[10px] text-muted-foreground/60">
          Powered by INAOE RAG
        </span>
      </div>
    </div>
  );
}
