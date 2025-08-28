// frontend/vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

export default defineConfig(({ mode }) => {
  // Local dev default → localhost; in containers set VITE_PROXY_TARGET=http://backend:8000
  const proxyTarget = process.env.VITE_PROXY_TARGET || "http://localhost:8000";

  return {
    server: {
      host: "::",
      port: 8080,
      proxy: {
        "/api": {
          target: proxyTarget, // ✅ use the env-driven target
          changeOrigin: true,
          secure: false,
          rewrite: (p) =>
            p.startsWith("/api/uploads") ||
            p.startsWith("/api/dashboards") ||
            p.startsWith("/api/metabase")
              ? p
              : p.replace(/^\/api/, "/api/v1"),
        },
      },
    },
    plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
    resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
  };
});
