import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnimatedBackground } from '@/components/ui-custom/AnimatedBackground';
import { ChatHeader } from '@/components/chat/ChatHeader';
import { Sidebar } from '@/components/chat/Sidebar';
import { WelcomeScreen } from '@/components/chat/WelcomeScreen';
import { MessageBubble } from '@/components/chat/MessageBubble';
import { ChatInput } from '@/components/chat/ChatInput';
import { useChat } from '@/hooks/useChat';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ArrowDown } from 'lucide-react';

function App() {
  const [selectedModel, setSelectedModel] = useState('gemini-1.5-flash');

  const {
    sessions,
    currentSession,
    currentSessionId,
    isLoading,
    createNewSession,
    selectSession,
    deleteSession,
    sendMessage,
  } = useChat(selectedModel);

  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [currentSession?.messages]);

  const handleSendMessage = async (content: string) => {
    await sendMessage(content);
  };

  const handleSuggestionClick = (text: string) => {
    sendMessage(text);
  };

  const hasMessages = currentSession && currentSession.messages.length > 0;
  const isEmptyChat = !hasMessages || (currentSession.messages.length === 1 && currentSession.messages[0].role === 'assistant');

  return (
    <div className="relative min-h-screen bg-white text-foreground overflow-hidden">
      {/* Animated background */}
      <AnimatedBackground />

      {/* Main layout */}
      <div className="flex h-screen relative z-10">
        {/* Sidebar */}
        <Sidebar
          sessions={sessions}
          currentSessionId={currentSessionId}
          onSelectSession={selectSession}
          onDeleteSession={deleteSession}
          onNewChat={createNewSession}
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
          selectedModel={selectedModel}
          onModelChange={setSelectedModel}
        />

        {/* Main content */}
        <div className="flex-1 flex flex-col h-full min-w-0 bg-white/80">
          {/* Header */}
          <ChatHeader
            onNewChat={createNewSession}
            onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
            isSidebarOpen={isSidebarOpen}
            title={currentSession?.title}
          />

          {/* Messages area */}
          <div className="flex-1 overflow-hidden relative">
            <ScrollArea className="h-full">
              <div className="max-w-3xl mx-auto px-4 py-6">
                <AnimatePresence mode="wait">
                  {isEmptyChat ? (
                    <motion.div
                      key="welcome"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <WelcomeScreen onSuggestionClick={handleSuggestionClick} />
                    </motion.div>
                  ) : (
                    <motion.div
                      key="messages"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="space-y-6"
                    >
                      {currentSession?.messages.map((message) => (
                        <MessageBubble
                          key={message.id}
                          message={message}
                        />
                      ))}
                      <div ref={messagesEndRef} />
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </ScrollArea>

            {/* Scroll to bottom button */}
            <AnimatePresence>
              {hasMessages && (
                <motion.button
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  onClick={() => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })}
                  className="absolute bottom-4 right-4 p-2 rounded-full bg-white border border-border shadow-inaoe hover:shadow-inaoe-lg hover:border-primary/30 transition-all"
                >
                  <ArrowDown className="w-4 h-4 text-primary" />
                </motion.button>
              )}
            </AnimatePresence>
          </div>

          {/* Input area */}
          <div className="border-t border-border/50 bg-white/90 backdrop-blur-sm">
            <div className="max-w-3xl mx-auto px-4 py-4">
              <ChatInput
                onSend={handleSendMessage}
                isLoading={isLoading}
                placeholder="Escribe tu mensaje o haz una pregunta sobre los documentos del INAOE..."
              />
            </div>
          </div>
        </div>
      </div>

      {/* Decorative elements */}
      <div className="fixed bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/20 to-transparent pointer-events-none" />
    </div>
  );
}

export default App;
