import { useCallback, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import {
  confirmMetricMappings,
  fetchMetricSuggestions,
  MetricConfirmPayload,
  MetricSuggestion,
} from "@/api/metrics";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/use-toast";
import { Loader2, Sparkles } from "lucide-react";

type ColumnState = {
  selectedMetricId?: number;
  confidence?: number;
};

const confidenceLabel = (value: number | undefined) => {
  if (!value && value !== 0) return "Unknown";
  if (value >= 0.75) return "High";
  if (value >= 0.5) return "Medium";
  return "Low";
};

const MetricMapping = () => {
  const [params] = useSearchParams();
  const datasetId = params.get("datasetId") ?? "";
  const [columnState, setColumnState] = useState<Record<string, ColumnState>>({});
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["metric-suggestions", datasetId],
    queryFn: () => fetchMetricSuggestions(datasetId),
    enabled: Boolean(datasetId),
    onSuccess(response) {
      const nextState: Record<string, ColumnState> = {};
      response.columns.forEach((column) => {
        const suggestion = column.suggestions?.[0];
        if (suggestion) {
          nextState[column.column_name] = {
            selectedMetricId: suggestion.metric_id,
            confidence: suggestion.confidence,
          };
        }
      });
      setColumnState(nextState);
    },
  });

  const confirmMutation = useMutation({
    mutationFn: (payload: MetricConfirmPayload[]) => confirmMetricMappings(datasetId, payload),
    onSuccess(response) {
      toast({
        title: "Mappings confirmed",
        description: `Saved ${response.confirmed.length} column mappings.`,
      });
      queryClient.invalidateQueries({ queryKey: ["metric-suggestions", datasetId] });
    },
    onError(error: Error) {
      toast({
        title: "Failed to confirm mappings",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleSelect = useCallback((column: string, suggestion: MetricSuggestion) => {
    setColumnState((prev) => ({
      ...prev,
      [column]: {
        selectedMetricId: suggestion.metric_id,
        confidence: suggestion.confidence,
      },
    }));
  }, []);

  const handleConfirm = useCallback(() => {
    if (!data) return;
    const payload: MetricConfirmPayload[] = data.columns
      .map((column) => {
        const state = columnState[column.column_name];
        if (!state?.selectedMetricId) return undefined;
        return {
          column_name: column.column_name,
          metric_id: state.selectedMetricId,
          confidence: state.confidence,
          suggested_by_ai: true,
        };
      })
      .filter(Boolean) as MetricConfirmPayload[];
    confirmMutation.mutate(payload);
  }, [columnState, confirmMutation, data]);

  const readyToConfirm = useMemo(() => {
    if (!data) return false;
    return data.columns.every((column) => columnState[column.column_name]?.selectedMetricId);
  }, [columnState, data]);

  if (!datasetId) {
    return (
      <div className="mx-auto max-w-5xl space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Dataset required</CardTitle>
          </CardHeader>
          <CardContent>
            Provide a datasetId query string parameter to review metric mappings.
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex h-96 flex-col items-center justify-center gap-3 text-muted-foreground">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span>Fetching AI mapping suggestions…</span>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="mx-auto max-w-5xl space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Error loading suggestions</CardTitle>
          </CardHeader>
          <CardContent>
            We could not load mapping suggestions at this time. Refresh to try again.
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Metric mapping assistant</h1>
          <p className="text-sm text-muted-foreground">
            AI proposes matches between your dataset columns and our impact metric library. Review and confirm.
          </p>
        </div>
        <Button
          size="lg"
          className="gap-2"
          disabled={!readyToConfirm || confirmMutation.isPending}
          onClick={handleConfirm}
        >
          {confirmMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
          Confirm mappings
        </Button>
      </div>

      {data.columns.map((column) => {
        const state = columnState[column.column_name];
        return (
          <Card key={column.column_name} className="border-border/50 shadow-sm">
            <CardHeader className="flex flex-row items-start justify-between gap-6">
              <div>
                <CardTitle className="text-lg font-semibold">{column.column_name}</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Sample: {(column.summary?.sample_values as string[])?.join(", ") || "n/a"}
                </p>
              </div>
              <Badge variant="outline">
                Confidence: {confidenceLabel(state?.confidence)} {state?.confidence ? `(${Math.round((state.confidence ?? 0) * 100)}%)` : ""}
              </Badge>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">Select metric</p>
                  <Select
                    value={state?.selectedMetricId?.toString()}
                    onValueChange={(value) => {
                      const suggestion = column.suggestions.find((item) => item.metric_id.toString() === value);
                      if (suggestion) handleSelect(column.column_name, suggestion);
                    }}
                  >
                    <SelectTrigger className="w-full sm:w-80">
                      <SelectValue placeholder="Choose a metric" />
                    </SelectTrigger>
                    <SelectContent>
                      {column.suggestions.map((suggestion) => (
                        <SelectItem key={suggestion.metric_id} value={suggestion.metric_id.toString()}>
                          <div className="flex flex-col gap-1">
                            <span className="font-medium">{suggestion.metric_name}</span>
                            <span className="text-xs text-muted-foreground">
                              Score {(suggestion.confidence * 100).toFixed(0)}% • Similarity {(suggestion.similarity * 100).toFixed(0)}%
                            </span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center gap-2 rounded-full bg-primary/5 px-4 py-2 text-xs text-primary">
                  <Sparkles className="h-3.5 w-3.5" />
                  AI assist compares column statistics and SDG taxonomy.
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};

export default MetricMapping;
