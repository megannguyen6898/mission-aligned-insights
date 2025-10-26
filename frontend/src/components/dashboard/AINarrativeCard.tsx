import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface AINarrativeCardProps {
  title?: string;
  narrative: string;
  highlights?: string[];
  onRegenerate?: () => void;
}

export const AINarrativeCard: React.FC<AINarrativeCardProps> = ({
  title = 'AI narrative',
  narrative,
  highlights,
  onRegenerate,
}) => {
  return (
    <Card className="gradient-ai overflow-hidden rounded-2xl border border-primary/15 bg-primary/5 shadow-none">
      <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3 text-primary">
          <div className="rounded-2xl bg-primary/15 p-2 text-primary">
            <Sparkles className="h-5 w-5" aria-hidden />
          </div>
          <div>
            <CardTitle className="text-base font-semibold text-foreground">{title}</CardTitle>
            <CardDescription className="text-sm text-primary/80">
              Narrative intelligence summarises what changed and why.
            </CardDescription>
          </div>
        </div>
        {onRegenerate && (
          <Button
            onClick={onRegenerate}
            variant="outline"
            size="sm"
            className="rounded-full border-primary/40 bg-background/70 text-primary hover:bg-primary hover:text-primary-foreground"
          >
            Regenerate insight
          </Button>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm leading-relaxed text-primary/90">{narrative}</p>
        {highlights?.length ? (
          <div className="flex flex-wrap gap-2">
            {highlights.map((highlight) => (
              <span
                key={highlight}
                className="rounded-full border border-primary/30 bg-background/70 px-3 py-1 text-xs font-medium text-primary"
              >
                {highlight}
              </span>
            ))}
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
};
