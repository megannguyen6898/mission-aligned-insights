import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
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

  return (
    <div className="space-y-6">
      {/* Export Actions */}
      <Card className="soft-shadow-lg border-border/50 rounded-2xl">
        <CardContent className="p-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="space-y-1">
              <h3 className="text-lg font-semibold text-foreground">Export Reports</h3>
              <p className="text-sm text-muted-foreground">
                Download your impact reports for stakeholders
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Button
                onClick={onExportPDF}
                className="bg-primary hover:bg-primary/90"
              >
                <Download className="h-4 w-4 mr-2" />
                Export PDF
              </Button>
              <Button
                onClick={onExportExcel}
                variant="outline"
                className="border-primary text-primary hover:bg-primary hover:text-primary-foreground"
              >
                <Download className="h-4 w-4 mr-2" />
                Export Excel
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Report Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3 h-auto p-1 bg-muted/50 rounded-xl">
          <TabsTrigger
            value="sdg"
            className={cn(
              'rounded-lg py-3 text-sm font-medium transition-all',
              'data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-sm'
            )}
          >
            SDG Alignment
          </TabsTrigger>
          <TabsTrigger
            value="ops"
            className={cn(
              'rounded-lg py-3 text-sm font-medium transition-all',
              'data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-sm'
            )}
          >
            Operations
          </TabsTrigger>
          <TabsTrigger
            value="sroi"
            className={cn(
              'rounded-lg py-3 text-sm font-medium transition-all',
              'data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:shadow-sm'
            )}
          >
            SROI Analysis
          </TabsTrigger>
        </TabsList>

        {/* SDG Tab */}
        <TabsContent value="sdg" className="space-y-6">
          {sdgContent || (
            <Card className="soft-shadow border-border/50 rounded-2xl">
              <CardContent className="p-8 space-y-6">
                <div className="text-center space-y-4">
                  <FileText className="h-12 w-12 mx-auto text-primary" />
                  <div>
                    <h3 className="text-xl font-semibold mb-2">SDG Impact Report</h3>
                    <p className="text-muted-foreground leading-relaxed">
                      View how your activities align with UN Sustainable Development Goals
                    </p>
                  </div>
                </div>
                {/* Placeholder SDG Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[1, 2, 3, 4].map((n) => (
                    <div
                      key={n}
                      className="gradient-ai rounded-xl p-6 border border-primary/10 space-y-2"
                    >
                      <h4 className="font-semibold text-foreground">
                        SDG Goal {n}: Goal Title
                      </h4>
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        Brief insight about how your organization contributes to this goal.
                        This would include specific metrics and achievements.
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Operations Tab */}
        <TabsContent value="ops" className="space-y-6">
          {opsContent || (
            <Card className="soft-shadow border-border/50 rounded-2xl">
              <CardContent className="p-8">
                <div className="text-center space-y-4">
                  <FileText className="h-12 w-12 mx-auto text-primary" />
                  <div>
                    <h3 className="text-xl font-semibold mb-2">Operations Report</h3>
                    <p className="text-muted-foreground leading-relaxed">
                      Detailed operational metrics and performance indicators
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* SROI Tab */}
        <TabsContent value="sroi" className="space-y-6">
          {sroiContent || (
            <Card className="soft-shadow border-border/50 rounded-2xl">
              <CardContent className="p-8">
                <div className="text-center space-y-4">
                  <FileText className="h-12 w-12 mx-auto text-primary" />
                  <div>
                    <h3 className="text-xl font-semibold mb-2">SROI Analysis</h3>
                    <p className="text-muted-foreground leading-relaxed">
                      Social Return on Investment calculations and insights
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Privacy Note */}
      <div className="flex items-start gap-3 p-4 rounded-xl bg-muted/30 border border-border">
        <Lock className="h-5 w-5 text-muted-foreground flex-shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="text-sm font-medium text-foreground">Data Privacy & Security</p>
          <p className="text-xs text-muted-foreground leading-relaxed">
            All reports are generated securely and contain only aggregated, anonymized data
            unless you specifically include identifiable information. Your data is encrypted
            and never shared without your explicit consent.
          </p>
        </div>
      </div>
    </div>
  );
};
