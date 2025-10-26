// src/pages/auth/Login.tsx
import React from "react";
import type { AxiosError } from "axios";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link, useNavigate } from "react-router-dom";

import { loginUser, getMe } from "@/api/auth";
import { setAccessToken } from "@/lib/api";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";

const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});
type LoginFormData = z.infer<typeof loginSchema>;

const fromAxiosError = (error: unknown): string => {
  if (!error) return "Login failed";
  if (typeof error === "string") return error;
  const axiosError = error as AxiosError<{ detail?: string }>;
  return (
    axiosError.response?.data?.detail ??
    axiosError.message ??
    "Login failed"
  );
};

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = React.useState(false);

  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
    mode: "onSubmit",
  });

  const onSubmit = async (values: LoginFormData) => {
    form.clearErrors("root");
    setLoading(true);
    try {
      // 1) Authenticate
      const { data: tokens } = await loginUser({ email: values.email, password: values.password });

      // 2) Store tokens + set bearer for subsequent calls
      setAccessToken(tokens.access_token);
      localStorage.setItem("access_token", tokens.access_token);
      localStorage.setItem("refresh_token", tokens.refresh_token);

      // 3) (Optional) fetch user profile for your app state
      try {
        const me = await getMe();
        localStorage.setItem("user", JSON.stringify(me.data));
      } catch {
        /* non-fatal */
      }

      // 4) Begin workflow at Upload step
      navigate("/upload", { replace: true });
    } catch (err: unknown) {
      const msg = fromAxiosError(err);
      form.setError("root", { type: "server", message: msg });
      if (typeof err === "object" && err !== null) {
        console.error("Login error:", (err as AxiosError).response?.status, msg);
      } else {
        console.error("Login error:", msg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-background to-accent/10">
      <div className="mx-auto flex min-h-screen max-w-5xl items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid w-full gap-10 rounded-3xl border border-border/60 bg-card/90 p-10 shadow-2xl sm:grid-cols-[1.1fr_1fr]">
          <div className="hidden flex-col justify-between rounded-2xl border border-primary/20 bg-primary/10 p-8 text-primary sm:flex">
            <div className="space-y-4">
              <p className="text-sm font-semibold uppercase tracking-wide text-primary/80">
                ImpactView
              </p>
              <h2 className="text-3xl font-semibold leading-snug text-primary">
                Welcome back.
              </h2>
              <p className="text-sm leading-relaxed text-primary/80">
                Sign in to review fresh KPI cards, confirm mappings, and share reports with stakeholders.
              </p>
            </div>
            <div className="rounded-2xl border border-primary/20 bg-background/80 p-4 text-xs text-primary/80">
              Encrypted sessions, SOC2-ready, lineage preserved end to end.
            </div>
          </div>

          <Card className="soft-shadow border-border/60">
            <CardHeader className="space-y-2 text-left">
              <CardTitle className="text-2xl font-semibold text-foreground">Sign in</CardTitle>
              <CardDescription className="text-sm text-muted-foreground">
                Enter your email and password to access the impact workspace.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4" aria-busy={loading}>
                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Email</FormLabel>
                        <FormControl>
                          <Input
                            type="email"
                            inputMode="email"
                            autoComplete="email"
                            placeholder="you@example.com"
                            disabled={loading}
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="password"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Password</FormLabel>
                        <FormControl>
                          <Input
                            type="password"
                            autoComplete="current-password"
                            placeholder="Enter your password"
                            disabled={loading}
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* Root/server error (from API) */}
                  {form.formState.errors.root?.message && (
                    <p className="text-sm text-red-600">{form.formState.errors.root.message}</p>
                  )}

                  <Button type="submit" className="w-full rounded-full bg-primary py-5" disabled={loading}>
                    {loading ? "Signing in..." : "Sign In"}
                  </Button>
                </form>
              </Form>

              <div className="mt-6 text-center">
                <p className="text-sm text-muted-foreground">
                  Don't have an account?{" "}
                  <Link to="/signup" className="font-medium text-primary hover:text-primary/80">
                    Sign up
                  </Link>
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Login;
