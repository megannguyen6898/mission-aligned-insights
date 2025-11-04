import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

const placeholderRows = [
  { framework: "SDG", metric: "Goal 4 - Quality Education", status: "Pending" },
  { framework: "SROI", metric: "Social return multiple", status: "Coming soon" },
  { framework: "ESG", metric: "Governance maturity", status: "Roadmap" },
];

const ImpactBalanceSheetTab = () => {
  return (
    <div className="space-y-6">
      <Card className="border-dashed border-border/60 bg-muted/30">
        <CardHeader>
          <CardTitle>Impact balance sheet (preview)</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          This tab will consolidate SDG, SROI, and ESG frameworks into a unified balance sheet. Stakeholders will
          be able to reconcile financial, social, and environmental outcomes in one place. For now, placeholders help
          shape the next iteration.
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Framework snapshot</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-32">Framework</TableHead>
                <TableHead>Metric</TableHead>
                <TableHead className="w-32">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {placeholderRows.map((row) => (
                <TableRow key={`${row.framework}-${row.metric}`}>
                  <TableCell className="font-medium">{row.framework}</TableCell>
                  <TableCell>{row.metric}</TableCell>
                  <TableCell className="text-muted-foreground">{row.status}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default ImpactBalanceSheetTab;
