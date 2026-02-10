import { motion } from 'framer-motion';

export function AnimatedBackground() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none bg-white">
      {/* Subtle blue gradient orbs */}
      <motion.div
        className="absolute -top-[30%] -right-[20%] w-[60%] h-[60%] rounded-full"
        style={{
          background: 'radial-gradient(circle, hsl(220 85% 28% / 0.04) 0%, transparent 70%)',
        }}
        animate={{
          x: [0, -30, 0],
          y: [0, 20, 0],
          scale: [1, 1.05, 1],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
      <motion.div
        className="absolute -bottom-[30%] -left-[20%] w-[60%] h-[60%] rounded-full"
        style={{
          background: 'radial-gradient(circle, hsl(200 80% 50% / 0.03) 0%, transparent 70%)',
        }}
        animate={{
          x: [0, 30, 0],
          y: [0, -20, 0],
          scale: [1, 1.08, 1],
        }}
        transition={{
          duration: 30,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
      
      {/* Very subtle grid pattern */}
      <div 
        className="absolute inset-0 opacity-[0.015]"
        style={{
          backgroundImage: `
            linear-gradient(hsl(220 85% 28%) 1px, transparent 1px),
            linear-gradient(90deg, hsl(220 85% 28%) 1px, transparent 1px)
          `,
          backgroundSize: '60px 60px',
        }}
      />
      
      {/* Top accent line */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary/30 to-transparent" />
    </div>
  );
}
