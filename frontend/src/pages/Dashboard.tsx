import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { listDashboards, getSignedDashboard } from "@/api/metabase";
import { Link } from "react-router-dom";

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
      <Card>
        <CardHeader>
          <CardTitle>No dashboards available</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-2">Upload some data to see your metrics.</p>
          <Link to="/upload" className="text-blue-600 underline">
            Go to Upload
          </Link>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
      <Select value={selected?.toString()} onValueChange={(v) => setSelected(Number(v))}>
        <SelectTrigger className="w-[250px]">
          <SelectValue placeholder="Select dashboard" />
        </SelectTrigger>
        <SelectContent>
          {dashboards.map((d) => (
            <SelectItem key={d.id} value={d.id.toString()}>
              {d.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {embedUrl && (
        <iframe
          src={embedUrl}
          className="w-full h-[600px] border rounded"
          allowFullScreen
        />
      )}
    </div>
  );
};

export default Dashboard;
