import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface ChartBlockProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  aiNarrative?: string;
  className?: string;
}

export const ChartBlock: React.FC<ChartBlockProps> = ({
  title,
  description,
  children,
  aiNarrative,
  className
}) => {
  return (
    <Card className={cn('soft-shadow border-border/50 rounded-2xl', className)}>
      <CardHeader className="space-y-1 pb-4">
        <CardTitle className="text-xl">{title}</CardTitle>
        {description && (
          <CardDescription className="text-base leading-relaxed">
            {description}
          </CardDescription>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="rounded-xl overflow-hidden">
          {children}
        </div>
        {aiNarrative && (
          <div className="gradient-ai rounded-xl p-4 space-y-2 border border-primary/10">
            <div className="flex items-center gap-2 text-sm font-medium text-foreground">
              <svg className="h-4 w-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              AI Insight
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {aiNarrative}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
