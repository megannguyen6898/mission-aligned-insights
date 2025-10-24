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
    <Card className={cn('soft-shadow-lg border-border/50', className)}>
      <CardContent className="p-6 space-y-2">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          {icon && <div className="text-muted-foreground">{icon}</div>}
        </div>
        <div className="space-y-1">
          <p className="text-4xl font-semibold tracking-tight text-foreground">
            {value}
          </p>
          {trend && (
            <div className={cn('flex items-center gap-1 text-sm', trendColor)}>
              <TrendIcon className="h-4 w-4" />
              <span className="font-medium">{trend.value}</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
