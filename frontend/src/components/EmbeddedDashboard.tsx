import { useEffect, useState } from "react";
import api from "@/services/api";

interface EmbeddedDashboardProps {
  slug: string;
  height?: number | string;
}

const METABASE_SITE_URL = import.meta.env.VITE_METABASE_SITE_URL || "";

const EmbeddedDashboard = ({ slug, height = 800 }: EmbeddedDashboardProps) => {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const fetchToken = async () => {
      try {
        const res = await api.get(`/dashboards/${slug}/embed-token`);
        setToken(res.data.token);
      } catch (err) {
        console.error("Failed to load dashboard token", err);
      }
    };
    fetchToken();
  }, [slug]);

  if (!token) {
    return <div>Loading...</div>;
  }

  const src = `${METABASE_SITE_URL}/embed/dashboard/${token}#bordered=false&titled=false`;

  return (
    <iframe
      src={src}
      frameBorder="0"
      width="100%"
      height={height}
      allowTransparency
    />
  );
};

export default EmbeddedDashboard;
