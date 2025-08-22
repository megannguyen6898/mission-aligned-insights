import axios from "axios";

// All requests go to /api, which Vite proxies to your backend /api/v1
export const api = axios.create({
  baseURL: "/api",
  // withCredentials: true, // only if you use cookie/session auth
});

let accessToken: string | null = null;
export function setAccessToken(t: string | null) { accessToken = t; }
api.interceptors.request.use(cfg => {
  if (accessToken) cfg.headers.Authorization = `Bearer ${accessToken}`;
  return cfg;
});