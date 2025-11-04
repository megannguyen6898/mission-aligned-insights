import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import type { CorrelationResult, SDGGoalSuggestion } from "@/api/metrics";

type Props = {
  goal: SDGGoalSuggestion;
  correlations: CorrelationResult[];
  narrative?: string;
};

export const SDGGoalTile = ({ goal, correlations, narrative }: Props) => {
  const filteredCorrelations = correlations.filter((entry) =>
    goal.targets.some((target) => target.indicators.some((indicator) => indicator.metric_id === entry.metric_id)),
  );

  return (
    <Card className="h-full border-border/50 shadow-sm">
      <CardHeader className="space-y-1">
        <CardTitle className="flex items-center gap-2 text-base">
          <Badge style={{ backgroundColor: goal.goal_color ?? undefined }} className="text-white">
            Goal {goal.goal_number}
          </Badge>
          <span>{goal.goal_title}</span>
        </CardTitle>
        <p className="text-xs text-muted-foreground">Alignment score {(goal.score * 100).toFixed(0)}%</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <p className="text-sm font-medium">Key indicators</p>
          <ul className="space-y-1 text-sm text-muted-foreground">
            {goal.targets.flatMap((target) =>
              target.indicators.map((indicator) => (
                <li key={indicator.indicator_id}>
                  Target {target.target_code} · Indicator {indicator.indicator_code} — {indicator.indicator_title}
                </li>
              )),
            )}
          </ul>
        </div>

        <Separator />

        <div className="space-y-3">
          <p className="text-sm font-medium">Correlation insights</p>
          {filteredCorrelations.length === 0 ? (
            <p className="text-sm text-muted-foreground">No correlations computed for this goal yet.</p>
          ) : (
            <ul className="space-y-2 text-sm text-muted-foreground">
              {filteredCorrelations.map((result) => (
                <li key={result.correlation_id} className="flex flex-col">
                  <span className="font-medium text-foreground">
                    Metric {result.metric_id} vs {result.independent_variable}
                  </span>
                  <span>
                    r={result.r_value.toFixed(2)} · {result.direction} · confidence {(result.confidence * 100).toFixed(0)}%
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {narrative && (
          <div className="rounded-md bg-muted/40 p-4 text-sm leading-relaxed text-muted-foreground">
            {narrative}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default SDGGoalTile;
