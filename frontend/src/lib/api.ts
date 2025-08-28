import axios from "axios";
import { toast } from "@/hooks/use-toast";

// All requests go to /api, which Vite proxies to your backend /api/v1
export const api = axios.create({
  baseURL: "/api",
  withCredentials: true,
});

let accessToken: string | null = null;
export function setAccessToken(t: string | null) { accessToken = t; }
api.interceptors.request.use(cfg => {
  if (accessToken) cfg.headers.Authorization = `Bearer ${accessToken}`;
  return cfg;
});

api.interceptors.response.use(
  res => res,
  err => {
    const detail = err?.response?.data?.detail;
    let message = "An unexpected error occurred";
    if (detail) {
      if (typeof detail === "string") {
        message = detail;
      } else if (detail.sheet && Array.isArray(detail.missing)) {
        message = `Sheet "${detail.sheet}" is missing required columns: ${detail.missing.join(", ")}`;
      }
    } else if (err.message) {
      message = err.message;
    }
    toast({
      title: "Request failed",
      description: message,
      variant: "destructive",
    });
    return Promise.reject(err);
  }
);
