import { motion } from 'framer-motion';
import { FileText, ExternalLink, Quote } from 'lucide-react';
import type { Source } from '@/types';

interface SourceCardProps {
  source: Source;
  index: number;
}

export function SourceCard({ source, index }: SourceCardProps) {
  const relevancePercent = Math.round(source.relevance * 100);
  
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1, duration: 0.3 }}
      className="source-card relative p-3 rounded-xl bg-white border border-border hover:border-primary/30 shadow-sm"
    >
      {/* Relevance indicator */}
      <div className="absolute top-3 right-3 flex items-center gap-1.5">
        <div className="flex items-center gap-1">
          <div 
            className="h-1.5 w-8 rounded-full bg-secondary overflow-hidden"
          >
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${relevancePercent}%` }}
              transition={{ delay: 0.5 + index * 0.1, duration: 0.5 }}
              className="h-full rounded-full bg-gradient-to-r from-primary to-accent"
            />
          </div>
          <span className="text-[10px] text-muted-foreground font-medium">{relevancePercent}%</span>
        </div>
      </div>

      {/* Header */}
      <div className="flex items-start gap-2 pr-20">
        <div className="flex-shrink-0 w-7 h-7 rounded-lg bg-primary/10 flex items-center justify-center">
          <FileText className="w-3.5 h-3.5 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-xs font-semibold text-foreground truncate pr-2">
            {source.title}
          </h4>
          {source.metadata && (
            <div className="flex items-center gap-2 mt-0.5 text-[10px] text-muted-foreground">
              {source.metadata.author && (
                <span className="truncate">{source.metadata.author}</span>
              )}
              {source.metadata.page && (
                <span className="flex items-center gap-0.5">
                  <span className="w-0.5 h-0.5 rounded-full bg-muted-foreground" />
                  Pág. {source.metadata.page}
                </span>
              )}
              {source.metadata.date && (
                <span className="flex items-center gap-0.5">
                  <span className="w-0.5 h-0.5 rounded-full bg-muted-foreground" />
                  {source.metadata.date}
                </span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Content preview */}
      <div className="mt-2 pl-9">
        <div className="relative">
          <Quote className="absolute -left-4 top-0 w-3 h-3 text-primary/30" />
          <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
            {source.content}
          </p>
        </div>
      </div>

      {/* Action buttons */}
      {source.metadata?.url && (
        <div className="mt-2 pl-9 flex justify-end">
          <a
            href={source.metadata.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-[10px] text-primary hover:text-primary/80 transition-colors font-medium"
          >
            Ver fuente
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      )}
    </motion.div>
  );
}
