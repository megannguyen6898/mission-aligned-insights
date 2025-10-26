// frontend/vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

export default defineConfig(async ({ mode }) => {
  // Local dev default → localhost; in containers set VITE_PROXY_TARGET=http://backend:8000
  const proxyTarget = process.env.VITE_PROXY_TARGET || "http://localhost:8000";
  const plugins = [react()];

  if (mode === "development") {
    try {
      const { componentTagger } = await import("lovable-tagger");
      plugins.push(componentTagger());
    } catch (error) {
      console.warn("lovable-tagger not installed, skipping component tagging.");
    }
  }

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
            p.startsWith("/api/analytics") ||
            p.startsWith("/api/report")
              ? p
              : p.replace(/^\/api/, "/api/v1"),
        },
      },
    },
    plugins,
    resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
    test: {
      environment: "jsdom",
      globals: true,
      setupFiles: [path.resolve(__dirname, "./src/__tests__/setup.ts")],
      css: true,
    },
  };
});
