import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface ChartBlockProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
  children: React.ReactNode;
}

export const ChartBlock: React.FC<ChartBlockProps> = ({ title, description, action, className, children }) => {
  return (
    <Card
      className={cn(
        'rounded-2xl border border-border/60 bg-card/95 soft-shadow',
        'bg-[radial-gradient(circle_at_top,_rgba(6,182,212,0.05),_transparent_55%)]',
        className
      )}
    >
      <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <CardTitle className="text-base font-semibold text-foreground">{title}</CardTitle>
          {description && (
            <CardDescription className="text-sm leading-relaxed text-muted-foreground">
              {description}
            </CardDescription>
          )}
        </div>
        {action}
      </CardHeader>
      <CardContent className="relative">
        <div className="absolute inset-0 pointer-events-none">
          <div className="h-full w-full rounded-2xl border border-white/10 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]" />
        </div>
        <div className="relative">{children}</div>
      </CardContent>
    </Card>
  );
};
