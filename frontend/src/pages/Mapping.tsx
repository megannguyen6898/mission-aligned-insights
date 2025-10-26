import React, { useMemo, useState } from "react";
import { PageHeader } from "@/components/layout/PageHeader";
import { MappingTable } from "@/components/mapping/MappingTable";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { AlertCircle, Sparkles } from "lucide-react";

interface MappingRow {
  sourceColumn: string;
  suggestedMapping: string;
  confidence: number;
  currentMapping?: string;
}

const initialMappings: MappingRow[] = [
  {
    sourceColumn: "Clients Reached",
    suggestedMapping: "Beneficiaries Served",
    confidence: 0.86,
  },
  {
    sourceColumn: "Program Area",
    suggestedMapping: "Program Name",
    confidence: 0.73,
  },
  {
    sourceColumn: "Reporting Period",
    suggestedMapping: "Date",
    confidence: 0.62,
  },
  {
    sourceColumn: "Province",
    suggestedMapping: "Location",
    confidence: 0.55,
  },
  {
    sourceColumn: "Outcome Score",
    suggestedMapping: "Outcome",
    confidence: 0.91,
  },
];

const Mapping: React.FC = () => {
  const [rows, setRows] = useState<MappingRow[]>(initialMappings);
  const [advancedMode, setAdvancedMode] = useState(false);
  const [aiAssistEnabled, setAiAssistEnabled] = useState(true);

  const readyToConfirm = useMemo(() => {
    return rows.every((row) => {
      if (row.confidence >= 0.7) {
        return true;
      }
      return Boolean(row.currentMapping);
    });
  }, [rows]);

  return (
    <div className="space-y-10">
      <PageHeader
        title="Confirm smart mappings"
        description="We mapped your columns to the ImpactView data model. Review AI suggestions, confirm what looks right, and tweak anything that needs more context. You stay in control."
        actions={
          <Button
            size="lg"
            className="rounded-full bg-primary px-6 text-sm font-semibold"
            disabled={!readyToConfirm}
          >
            Confirm mappings
          </Button>
        }
      />

      <div className="grid gap-8 xl:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-6">
          <div className="flex flex-col gap-3 rounded-2xl border border-border/60 bg-muted/30 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-foreground">AI Assist suggestions</p>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Toggle to use heuristic recommendations for column mappings.
              </p>
            </div>
            <Switch
              checked={aiAssistEnabled}
              onCheckedChange={setAiAssistEnabled}
              aria-label="AI Assist toggle"
            />
          </div>

          <Card className="rounded-2xl border-border/60 bg-card soft-shadow">
            <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="space-y-1">
                <CardTitle className="text-lg font-semibold text-foreground">Structured mapping</CardTitle>
                <CardDescription className="text-sm text-muted-foreground leading-relaxed">
                  “We think Clients Reached = Beneficiaries Served.” Confirm each suggestion or choose a better fit.
                </CardDescription>
              </div>
              <div className="flex items-center gap-2 rounded-full border border-border/60 bg-muted/40 px-3 py-1.5 text-xs text-muted-foreground">
                <Sparkles className="h-3.5 w-3.5 text-primary" />
                AI confidence reflects past data quality and column names.
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <MappingTable
                mappings={rows}
                onMappingChange={(column, value) =>
                  setRows((prev) =>
                    prev.map((row) =>
                      row.sourceColumn === column ? { ...row, currentMapping: value } : row
                    )
                  )
                }
                aiEnabled={aiAssistEnabled}
              />

              <div className="flex flex-col gap-4 rounded-2xl border border-border/60 bg-muted/30 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-semibold text-foreground">Advanced mapping</p>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Unlock calculated fields, conditional rules, and data validations. Toggle on to preview upcoming capabilities.
                  </p>
                </div>
                <Switch checked={advancedMode} onCheckedChange={setAdvancedMode} aria-label="Advanced mapping toggle" />
              </div>
            </CardContent>
          </Card>

          {advancedMode && (
            <Card className="rounded-2xl border-primary/15 bg-primary/5 soft-shadow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base font-semibold text-primary">
                  <Sparkles className="h-4 w-4" />
                  Advanced mapping preview
                </CardTitle>
                <CardDescription className="text-sm text-primary/80">
                  Configure transformations before they ship. Provide feedback to shape the roadmap.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 text-sm text-primary/80">
                <p>• Apply conditional logic (e.g., “If blank, use last known value”).</p>
                <p>• Set up multi-column merges and friendly display names.</p>
                <p>• Flag low-confidence matches for human review before ingestion.</p>
              </CardContent>
            </Card>
          )}
        </div>

        <div className="space-y-6">
          <Card className="rounded-2xl border-border/60 bg-card/90 soft-shadow">
            <CardHeader>
              <CardTitle className="text-base font-semibold text-foreground">AI mapping summary</CardTitle>
              <CardDescription>
                {aiAssistEnabled
                  ? "Everything looks consistent with your prior uploads."
                  : "AI Assist is off. Review saved mappings before continuing."}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-sm leading-relaxed text-muted-foreground">
              <p>
                4 of 5 columns match confidently with the global impact data model. “Province” is low confidence because past uploads used “Region.”
                Confirm the suggestion or choose another field.
              </p>
              <div className="rounded-2xl border border-border/60 bg-muted/30 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground/80">
                  Data lineage
                </p>
                <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
                  Every mapping is auditable. Changes appear in the activity trail with who approved them, so stakeholders can trust the transformations powering their dashboards.
                </p>
              </div>
              <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-muted-foreground/80">
                <Badge variant="secondary" className="rounded-full bg-primary/10 text-primary">
                  Confidence
                </Badge>
                <span>High (≥ 0.8) • Medium (0.5–0.79) • Low (&lt; 0.5)</span>
              </div>
            </CardContent>
          </Card>

          <Card className="rounded-2xl border-destructive/20 bg-destructive/5 soft-shadow">
            <CardHeader className="space-y-2">
              <CardTitle className="flex items-center gap-2 text-base font-semibold text-destructive">
                <AlertCircle className="h-4 w-4" />
                Lineage alerts
              </CardTitle>
              <CardDescription className="text-sm text-destructive/80">
                1 field changed since your last upload. Review before generating reports.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-destructive/80">
              <p>“Province” was previously mapped to “Region.” Keeping it aligned improves trend comparisons.</p>
              <TooltipProvider delayDuration={0}>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="ghost" className="w-full justify-start px-0 text-sm text-destructive hover:text-destructive focus-visible:ring-destructive">
                      View mapping history
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    Track who changed what and when, tied to ingest batches.
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </CardContent>
          </Card>
        </div>
      </div>

      {!readyToConfirm ? (
        <div className="rounded-2xl border border-accent/40 bg-accent/15 px-4 py-3 text-sm text-foreground soft-shadow">
          Double-check low-confidence mappings or leave a note for teammates so they know what changed.
        </div>
      ) : (
        <div className="rounded-2xl border border-primary/30 bg-primary/10 px-4 py-3 text-sm text-primary soft-shadow">
          Everything looks good. Confirm mappings to unlock refreshed dashboards and reports.
        </div>
      )}
    </div>
  );
};

export default Mapping;
