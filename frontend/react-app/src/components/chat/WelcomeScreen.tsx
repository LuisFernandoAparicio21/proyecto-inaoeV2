import { motion } from 'framer-motion';
import { Brain, FileSearch, BookMarked, MessageSquare, BookOpen, Database, Telescope } from 'lucide-react';

interface WelcomeScreenProps {
  onSuggestionClick?: (text: string) => void;
}

export function WelcomeScreen({ onSuggestionClick }: WelcomeScreenProps) {
  const features = [
    {
      icon: Brain,
      title: 'IA Avanzada',
      description: 'Respuestas inteligentes basadas en documentos científicos',
    },
    {
      icon: FileSearch,
      title: 'Búsqueda Semántica',
      description: 'Encuentra información relevante al instante',
    },
    {
      icon: BookMarked,
      title: 'Fuentes Citadas',
      description: 'Referencias académicas con documento y página exacta',
    },
  ];

  const suggestions = [
    { icon: BookOpen, text: 'Resume el documento principal', category: 'Resumen' },
    { icon: Database, text: '¿Qué datos contiene esta base de conocimiento?', category: 'Explorar' },
    { icon: MessageSquare, text: 'Explica los conceptos clave', category: 'Aprender' },
    { icon: FileSearch, text: 'Busca información específica sobre...', category: 'Buscar' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ staggerChildren: 0.1, delayChildren: 0.2 }}
      className="flex flex-col items-center justify-center min-h-[60vh] px-4 py-8"
    >
      {/* INAOE Logo */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="relative mb-6"
      >
        <motion.div
          animate={{
            scale: [1, 1.02, 1],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="w-28 h-28 flex items-center justify-center"
        >
          <img
            src="/inaoe-logo.png"
            alt="INAOE Logo"
            className="w-full h-full object-contain"
          />
        </motion.div>
      </motion.div>

      {/* Title */}
      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="text-3xl md:text-4xl font-bold text-center mb-2"
      >
        <span className="text-primary">INAOE</span>
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut', delay: 0.05 }}
        className="text-lg text-muted-foreground text-center mb-3"
      >
        Instituto Nacional de Astrofísica, Óptica y Electrónica
      </motion.p>

      {/* Subtitle */}
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut', delay: 0.1 }}
        className="text-muted-foreground text-center max-w-md mb-10 flex items-center gap-2 justify-center"
      >
        <Telescope className="w-4 h-4 text-primary" />
        Asistente Inteligente de Investigación
      </motion.p>

      {/* Features */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut', delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10 w-full max-w-2xl"
      >
        {features.map((feature, index) => (
          <motion.div
            key={index}
            whileHover={{ scale: 1.02, y: -2 }}
            className="p-4 rounded-xl bg-secondary/50 border border-border hover:border-primary/30 transition-all"
          >
            <feature.icon className="w-5 h-5 text-primary mb-2" />
            <h3 className="text-sm font-semibold mb-1">{feature.title}</h3>
            <p className="text-xs text-muted-foreground">{feature.description}</p>
          </motion.div>
        ))}
      </motion.div>

      {/* Suggestions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut', delay: 0.3 }}
        className="w-full max-w-2xl"
      >
        <p className="text-xs text-muted-foreground text-center mb-3">
          Prueba con alguna de estas sugerencias
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {suggestions.map((suggestion, index) => (
            <motion.button
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease: 'easeOut', delay: 0.3 + index * 0.05 }}
              whileHover={{ scale: 1.01, x: 2 }}
              whileTap={{ scale: 0.99 }}
              onClick={() => onSuggestionClick?.(suggestion.text)}
              className="flex items-center gap-3 p-3 rounded-xl bg-white border border-border hover:border-primary/30 hover:bg-secondary/30 transition-all text-left group shadow-sm hover:shadow-inaoe"
            >
              <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                <suggestion.icon className="w-4 h-4 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-foreground truncate">{suggestion.text}</p>
                <p className="text-[10px] text-muted-foreground">{suggestion.category}</p>
              </div>
            </motion.button>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
}
