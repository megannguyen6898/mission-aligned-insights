import React, { useMemo, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileText, Download, Lock } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ReportTabsProps {
  sdgContent?: React.ReactNode;
  opsContent?: React.ReactNode;
  sroiContent?: React.ReactNode;
  onExportPDF?: () => void;
  onExportExcel?: () => void;
}

export const ReportTabs: React.FC<ReportTabsProps> = ({
  sdgContent,
  opsContent,
  sroiContent,
  onExportPDF,
  onExportExcel,
}) => {
  const [activeTab, setActiveTab] = useState('sdg');
  const defaultSdgCards = useMemo(
    () => [
      {
        title: 'SDG 4 • Quality Education',
        narrative:
          'Graduation rates hit 92% with mentorship starting earlier in the bootcamp journey. AI recommends expanding the peer mentor model.',
      },
      {
        title: 'SDG 5 • Gender Equality',
        narrative:
          'Women now represent 58% of cohort intake, closing the gap by 11 points year-on-year. Spotlight this in donor updates.',
      },
      {
        title: 'SDG 8 • Decent Work',
        narrative:
          'Micro-enterprise programme generated 180 jobs with 95% loan repayment. Highlight community leadership stories.',
      },
    ],
    []
  );

  return (
    <div className="space-y-6">
      <Card className="rounded-2xl border border-border/60 bg-card/95 soft-shadow">
        <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <CardTitle className="text-base font-semibold text-foreground">Export reports</CardTitle>
            <CardDescription className="text-sm text-muted-foreground leading-relaxed">
              PDF for boards, Excel for analysts. Both maintain lineage and confidence scores.
            </CardDescription>
          </div>
          <div className="flex items-center gap-3">
            <Button
              onClick={onExportPDF}
              className="rounded-full bg-primary px-4 text-sm font-semibold"
            >
              <Download className="mr-2 h-4 w-4" />
              Export PDF
            </Button>
            <Button
              onClick={onExportExcel}
              variant="outline"
              className="rounded-full border-primary/40 text-primary"
            >
              <Download className="mr-2 h-4 w-4" />
              Export Excel
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Report Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid h-auto w-full grid-cols-3 rounded-full border border-border/60 bg-muted/40 p-1">
          <TabsTrigger
            value="sdg"
            className={cn(
              'rounded-full py-3 text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
              'data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-sm'
            )}
          >
            SDG Alignment
          </TabsTrigger>
          <TabsTrigger
            value="ops"
            className={cn(
              'rounded-full py-3 text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
              'data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-sm'
            )}
          >
            Operations
          </TabsTrigger>
          <TabsTrigger
            value="sroi"
            className={cn(
              'rounded-full py-3 text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
              'data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-sm'
            )}
          >
            SROI Analysis
          </TabsTrigger>
        </TabsList>

        <TabsContent value="sdg" className="space-y-6">
          {sdgContent || (
            <Card className="rounded-2xl border border-primary/15 bg-primary/5 soft-shadow">
              <CardContent className="space-y-6 p-8">
                <div className="flex items-center gap-3">
                  <div className="rounded-2xl bg-primary/15 p-2 text-primary">
                    <FileText className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-foreground">SDG insight cards</h3>
                    <p className="text-sm text-primary/80 leading-relaxed">
                      Show how programmes roll up to the UN Sustainable Development Goals.
                    </p>
                  </div>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  {defaultSdgCards.map((card) => (
                    <div
                      key={card.title}
                      className="rounded-2xl border border-primary/20 bg-background/80 p-5 text-sm leading-relaxed text-primary/90 shadow-sm"
                    >
                      <p className="font-semibold text-primary">{card.title}</p>
                      <p className="mt-2 text-primary/80">{card.narrative}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="ops" className="space-y-6">
          {opsContent || (
            <Card className="rounded-2xl border border-border/60 bg-card/95 soft-shadow">
              <CardContent className="space-y-6 p-8 text-sm leading-relaxed text-muted-foreground">
                <div className="flex items-center gap-3 text-primary">
                  <FileText className="h-6 w-6" />
                  <h3 className="text-lg font-semibold text-foreground">Operational cadence</h3>
                </div>
                <div className="rounded-2xl border border-border/50 bg-muted/30 p-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground/80">
                    Programme health table
                  </p>
                  <div className="mt-4 overflow-hidden rounded-xl border border-border/60">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-muted/60 text-muted-foreground">
                        <tr>
                          <th className="px-4 py-3 font-semibold uppercase tracking-wide">Programme</th>
                          <th className="px-4 py-3 font-semibold uppercase tracking-wide">Reach</th>
                          <th className="px-4 py-3 font-semibold uppercase tracking-wide">On-track</th>
                          <th className="px-4 py-3 font-semibold uppercase tracking-wide">Confidence</th>
                        </tr>
                      </thead>
                      <tbody>
                        {[
                          { name: 'Youth Skills Initiative', reach: '1,240', track: 'Green', confidence: 'High (0.86)' },
                          { name: 'Community Entrepreneurship', reach: '320', track: 'Amber', confidence: 'Medium (0.71)' },
                          { name: 'Climate Innovation Fund', reach: '540', track: 'Green', confidence: 'High (0.84)' },
                        ].map((row, idx) => (
                          <tr
                            key={row.name}
                            className={cn(
                              'transition-colors hover:bg-accent/40',
                              idx % 2 === 0 ? 'bg-background' : 'bg-muted/20'
                            )}
                          >
                            <td className="px-4 py-3 font-medium text-foreground">{row.name}</td>
                            <td className="px-4 py-3">{row.reach}</td>
                            <td className="px-4 py-3">{row.track}</td>
                            <td className="px-4 py-3">
                              <span className="rounded-full border border-primary/30 bg-primary/10 px-2 py-1 text-[11px] font-medium text-primary">
                                {row.confidence}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
                <p>Include qualitative notes to explain outliers and contextual nuance before sharing with leadership.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="sroi" className="space-y-6">
          {sroiContent || (
            <Card className="rounded-2xl border border-border/60 bg-card/95 soft-shadow">
              <CardContent className="space-y-6 p-8">
                <div className="flex items-center gap-3 text-primary">
                  <FileText className="h-6 w-6" />
                  <h3 className="text-lg font-semibold text-foreground">SROI analysis</h3>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  {[
                    { label: 'Financial leverage', value: '$1 → $4.20', note: 'Weighted across programmes with full data coverage.' },
                    { label: 'Community outcomes', value: '89% positive', note: 'Based on post-programme surveys (n = 812).' },
                    { label: 'Cost per beneficiary', value: '$162', note: 'Down 14% after automation of intake workflows.' },
                    { label: 'Payback period', value: '10 months', note: 'Projected with conservative retention assumptions.' },
                  ].map((item) => (
                    <div key={item.label} className="rounded-2xl border border-border/60 bg-muted/30 p-5">
                      <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground/80">
                        {item.label}
                      </p>
                      <p className="mt-2 text-xl font-semibold text-foreground">{item.value}</p>
                      <p className="mt-1 text-xs text-muted-foreground">{item.note}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Privacy Note */}
      <Card className="rounded-2xl border border-border/60 bg-muted/30 soft-shadow">
        <CardContent className="flex items-start gap-3 p-5 text-xs leading-relaxed text-muted-foreground">
          <Lock className="mt-0.5 h-5 w-5 flex-shrink-0 text-muted-foreground" />
          <div>
            <p className="text-sm font-semibold text-foreground">Data privacy & security</p>
            <p className="mt-1">
              Reports only include aggregated, anonymised data unless you explicitly opt in. Every export is tagged with lineage metadata for auditing.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
