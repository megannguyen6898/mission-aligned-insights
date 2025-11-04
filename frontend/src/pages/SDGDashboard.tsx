import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import {
  fetchAnalysisResults,
  fetchSDGSuggestions,
  runImpactAnalysis,
  AnalysisResultsResponse,
  SDGSuggestResponse,
} from "@/api/metrics";
import { SDGGoalTile } from "@/components/dashboard/SDGGoalTile";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/use-toast";
import { Loader2 } from "lucide-react";

const SDGDashboard = () => {
  const [params] = useSearchParams();
  const datasetId = params.get("datasetId") ?? "";
  const [variables, setVariables] = useState<string>("impact_score,spend");
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const suggestionsQuery = useQuery<SDGSuggestResponse>({
    queryKey: ["sdg-suggestions", datasetId],
    queryFn: () => fetchSDGSuggestions(datasetId),
    enabled: Boolean(datasetId),
  });

  const correlationsQuery = useQuery<AnalysisResultsResponse>({
    queryKey: ["analysis-results", datasetId],
    queryFn: () => fetchAnalysisResults(datasetId),
    enabled: Boolean(datasetId),
  });

  const runAnalysisMutation = useMutation({
    mutationFn: () => runImpactAnalysis(datasetId, variables.split(",").map((value) => value.trim()).filter(Boolean)),
    onSuccess() {
      toast({
        title: "Analysis queued",
        description: "Correlation job submitted. Refresh in a moment to see updated results.",
      });
      queryClient.invalidateQueries({ queryKey: ["analysis-results", datasetId] });
    },
    onError(error: Error) {
      toast({
        title: "Unable to run analysis",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const correlations = correlationsQuery.data?.results ?? [];
  const isLoading = suggestionsQuery.isLoading || correlationsQuery.isLoading;

  if (!datasetId) {
    return (
      <div className="mx-auto max-w-5xl space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Dataset required</CardTitle>
          </CardHeader>
          <CardContent>Provide a datasetId query parameter to explore SDG intelligence.</CardContent>
        </Card>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex h-96 flex-col items-center justify-center gap-3 text-muted-foreground">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span>Generating SDG impact insights…</span>
      </div>
    );
  }

  if (suggestionsQuery.isError || !suggestionsQuery.data) {
    return (
      <div className="mx-auto max-w-5xl space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Error loading SDG insights</CardTitle>
          </CardHeader>
          <CardContent>We could not retrieve SDG data. Retry shortly.</CardContent>
        </Card>
      </div>
    );
  }

  const goals = suggestionsQuery.data.goals;
  const heatmapCells = useMemo(() => goals.map((goal) => ({
    label: `Goal ${goal.goal_number}`,
    value: Math.round(goal.score * 100),
    color: goal.goal_color ?? "#2563eb",
  })), [goals]);

  return (
    <div className="space-y-8">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">SDG impact intelligence</h1>
          <p className="text-sm text-muted-foreground">
            Visualise how your mapped metrics align with the UN Sustainable Development Goals and uncover directional correlations.
          </p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <Input
            value={variables}
            onChange={(event) => setVariables(event.target.value)}
            placeholder="Comma-separated independent variables"
            className="sm:w-72"
          />
          <Button onClick={() => runAnalysisMutation.mutate()} disabled={runAnalysisMutation.isPending}>
            {runAnalysisMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Run analysis"}
          </Button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {heatmapCells.map((cell) => (
          <Card key={cell.label} className="border-border/40">
            <CardContent className="flex flex-col items-start gap-2 py-4">
              <span className="text-xs text-muted-foreground">{cell.label}</span>
              <span className="text-2xl font-semibold" style={{ color: cell.color }}>
                {cell.value}%
              </span>
              <span className="text-xs text-muted-foreground">Alignment confidence</span>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {goals.map((goal) => (
          <SDGGoalTile
            key={goal.goal_id}
            goal={goal}
            correlations={correlations}
            narrative={`Goal ${goal.goal_number} spans ${goal.targets.length} targets. Highest signal aligns with ${goal.targets[0]?.target_title ?? "priority indicators"}.`}
          />
        ))}
      </div>
    </div>
  );
};

export default SDGDashboard;
