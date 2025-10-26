import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

interface KpiCardProps {
  title: string;
  value: string | number;
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    value: string;
  };
  icon?: React.ReactNode;
  className?: string;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  trend,
  icon,
  className
}) => {
  const TrendIcon = trend?.direction === 'up' 
    ? TrendingUp 
    : trend?.direction === 'down' 
    ? TrendingDown 
    : Minus;

  const trendColor = trend?.direction === 'up'
    ? 'text-primary'
    : trend?.direction === 'down'
    ? 'text-destructive'
    : 'text-muted-foreground';

  return (
    <Card
      className={cn(
        'rounded-2xl border border-border/60 bg-card/95 soft-shadow',
        'bg-[radial-gradient(circle_at_top,_rgba(6,182,212,0.08),_transparent_70%)]',
        className
      )}
    >
      <CardContent className="space-y-4 p-6">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground/80">
              {title}
            </p>
            <p className="mt-2 text-4xl font-semibold tracking-tight text-foreground sm:text-[2.75rem]">
              {value}
            </p>
          </div>
          {icon && (
            <div className="rounded-2xl border border-primary/20 bg-primary/10 p-2 text-primary">
              {icon}
            </div>
          )}
        </div>
        {trend && (
          <div className={cn('flex items-center gap-1 text-xs font-semibold uppercase tracking-wide', trendColor)}>
            <TrendIcon className="h-4 w-4" />
            <span>{trend.value}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
