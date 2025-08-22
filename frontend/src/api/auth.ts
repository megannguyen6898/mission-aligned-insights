import { api } from "@/lib/api";

export type RegisterBody = {
  email: string;
  name: string;
  password: string;
  // optional:
  organization_name?: string;
  mission?: string;
  audience?: string;
  sector?: string;
  region?: string;
  organization_size?: string;
  key_goals?: string;
};

export function registerUser(body: { email: string; name: string; password: string }) {
    return api.post("/auth/register", body);
  }
  export function loginUser(body: { email: string; password: string }) {
    return api.post("/auth/login", body);
  }

export function getMe() {
  return api.get("/users/me");
}
