import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Sparkles, ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MappingRow {
  sourceColumn: string;
  suggestedMapping: string;
  confidence: number;
  currentMapping?: string;
}

interface MappingTableProps {
  mappings: MappingRow[];
  onMappingChange?: (sourceColumn: string, newMapping: string) => void;
  standardColumns?: string[];
  aiEnabled?: boolean;
}

export const MappingTable: React.FC<MappingTableProps> = ({
  mappings,
  onMappingChange,
  standardColumns = ['Beneficiaries Served', 'Program Name', 'Date', 'Location', 'Outcome'],
  aiEnabled = true,
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 0.8) {
      return <Badge variant="secondary" className="rounded-full border border-primary/30 bg-primary/15 text-primary">High</Badge>;
    } else if (confidence >= 0.5) {
      return <Badge variant="secondary" className="rounded-full border border-accent/40 bg-accent/20 text-foreground">Medium</Badge>;
    }
    return <Badge variant="outline" className="rounded-full border border-destructive/40 text-destructive">Low</Badge>;
  };

  return (
    <Card className="soft-shadow-lg border-border/50 rounded-2xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className={cn('h-5 w-5', aiEnabled ? 'text-primary' : 'text-muted-foreground')} />
          {aiEnabled ? 'AI-assisted Mapping' : 'Manual Mapping'}
        </CardTitle>
        <CardDescription>
          {aiEnabled
            ? 'We think these columns match. Confirm or edit the mappings below.'
            : 'AI Assist is off. Map each column manually to continue.'}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Mapping Table */}
        <div className="overflow-hidden rounded-2xl border border-border/60">
          <table className="w-full text-sm">
            <thead className="bg-muted/40 text-muted-foreground">
              <tr className="uppercase tracking-wide text-[11px]">
                <th className="px-4 py-3 text-left font-semibold">
                  Your Column
                </th>
                <th className="px-4 py-3 text-left font-semibold">
                  Maps To
                </th>
                <th className="px-4 py-3 text-left font-semibold">
                  Confidence
                </th>
              </tr>
            </thead>
            <tbody>
              {mappings.map((mapping, idx) => (
                <tr
                  key={idx}
                  className={cn(
                    'transition-colors hover:bg-accent/40',
                    idx % 2 === 0 ? 'bg-background' : 'bg-muted/20'
                  )}
                >
                  <td className="px-4 py-4 text-sm font-medium text-foreground">
                    {mapping.sourceColumn}
                  </td>
                  <td className="px-4 py-4">
                    <Select
                      value={
                        (aiEnabled
                          ? mapping.currentMapping || mapping.suggestedMapping
                          : mapping.currentMapping || mapping.suggestedMapping) ?? undefined
                      }
                      onValueChange={(value) =>
                        onMappingChange?.(mapping.sourceColumn, value)
                      }
                    >
                      <SelectTrigger className="w-full rounded-xl border-border/60">
                        <SelectValue placeholder={aiEnabled ? "Confirm suggestion" : "Choose column"} />
                      </SelectTrigger>
                      <SelectContent className="bg-popover">
                        {standardColumns.map((col) => (
                          <SelectItem key={col} value={col}>
                            {col}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </td>
                  <td className="px-4 py-4">
                    {getConfidenceBadge(mapping.confidence)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Advanced Toggle */}
        <div className="pt-4 border-t border-border">
          <Button
            variant="ghost"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="w-full justify-between hover:bg-accent"
          >
            <span className="text-sm font-medium">Advanced Mapping Options</span>
            {showAdvanced ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </Button>

          {showAdvanced && (
            <div className="mt-4 p-4 rounded-xl bg-muted/30 border border-border space-y-3">
              <p className="text-sm text-muted-foreground">
                Advanced mapping features coming soon. Configure custom transformations,
                set data validation rules, and more.
              </p>
            </div>
          )}
        </div>

        {/* Data Lineage Note */}
        <div className="gradient-ai rounded-xl p-4 border border-primary/10">
          <p className="text-xs font-medium text-foreground mb-1">Data Lineage</p>
          <p className="text-xs text-muted-foreground leading-relaxed">
            All mappings are tracked and auditable. You can review the transformation
            history in your data settings.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
