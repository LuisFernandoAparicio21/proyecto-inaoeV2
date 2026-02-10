import { motion } from 'framer-motion';

export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1.5 px-4 py-3">
      <motion.div
        className="w-2 h-2 rounded-full bg-primary"
        animate={{
          scale: [0.6, 1, 0.6],
          opacity: [0.4, 1, 0.4],
        }}
        transition={{
          duration: 1.4,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 0,
        }}
      />
      <motion.div
        className="w-2 h-2 rounded-full bg-primary"
        animate={{
          scale: [0.6, 1, 0.6],
          opacity: [0.4, 1, 0.4],
        }}
        transition={{
          duration: 1.4,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 0.2,
        }}
      />
      <motion.div
        className="w-2 h-2 rounded-full bg-primary"
        animate={{
          scale: [0.6, 1, 0.6],
          opacity: [0.4, 1, 0.4],
        }}
        transition={{
          duration: 1.4,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: 0.4,
        }}
      />
    </div>
  );
}
