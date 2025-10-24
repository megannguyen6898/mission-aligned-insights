import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { KpiCard } from "@/components/common/KpiCard";
import { listDashboards, getSignedDashboard } from "@/api/metabase";
import { Link } from "react-router-dom";
import { Users, TrendingUp, Target, DollarSign } from "lucide-react";

interface DashboardInfo {
  id: number;
  name: string;
}

const Dashboard: React.FC = () => {
  const [dashboards, setDashboards] = useState<DashboardInfo[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [embedUrl, setEmbedUrl] = useState<string>("");

  useEffect(() => {
    async function load() {
      try {
        const { data } = await listDashboards();
        setDashboards(data || []);
        if (data && data.length > 0) {
          setSelected(data[0].id);
        }
      } catch (err) {
        console.error("Failed to load dashboards", err);
      }
    }
    load();
  }, []);

  useEffect(() => {
    if (selected == null) return;
    async function sign() {
      try {
        const { data } = await getSignedDashboard(selected);
        setEmbedUrl(data.url);
      } catch (err) {
        console.error("Failed to sign dashboard", err);
      }
    }
    sign();
  }, [selected]);

  if (dashboards.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-4xl font-bold text-foreground mb-2">Dashboard</h1>
          <p className="text-lg text-muted-foreground">View your impact metrics and insights</p>
        </div>
        <Card className="soft-shadow-lg border-border/50 rounded-2xl">
          <CardHeader>
            <CardTitle>No dashboards available</CardTitle>
            <CardDescription>Upload some data to start seeing your impact metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="bg-primary hover:bg-primary/90">
              <Link to="/upload">
                Go to Upload
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-foreground mb-2">Dashboard</h1>
          <p className="text-lg text-muted-foreground">Track your organization's impact in real-time</p>
        </div>
        <Select value={selected?.toString()} onValueChange={(v) => setSelected(Number(v))}>
          <SelectTrigger className="w-[280px] soft-shadow">
            <SelectValue placeholder="Select dashboard" />
          </SelectTrigger>
          <SelectContent className="bg-popover">
            {dashboards.map((d) => (
              <SelectItem key={d.id} value={d.id.toString()}>
                {d.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KpiCard
          title="Lives Impacted"
          value="2,547"
          trend={{ direction: 'up', value: '+12% from last month' }}
          icon={<Users className="h-5 w-5" />}
        />
        <KpiCard
          title="Programs Active"
          value="23"
          trend={{ direction: 'up', value: '+3 this quarter' }}
          icon={<Target className="h-5 w-5" />}
        />
        <KpiCard
          title="SDG Alignment"
          value="89%"
          trend={{ direction: 'neutral', value: 'Stable' }}
          icon={<TrendingUp className="h-5 w-5" />}
        />
        <KpiCard
          title="Social ROI"
          value="$4.2M"
          trend={{ direction: 'up', value: '+18% this year' }}
          icon={<DollarSign className="h-5 w-5" />}
        />
      </div>

      {/* Embedded Dashboard */}
      {embedUrl && (
        <Card className="soft-shadow-lg border-border/50 rounded-2xl overflow-hidden">
          <iframe
            src={embedUrl}
            className="w-full h-[70vh]"
            allowFullScreen
          />
        </Card>
      )}
    </div>
  );
};

export default Dashboard;
