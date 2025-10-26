// src/pages/auth/Signup.tsx
import React from "react";
import type { AxiosError } from "axios";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "@/api/auth";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";

const signupSchema = z
  .object({
    name: z.string().min(2, "Name must be at least 2 characters"),
    email: z.string().email("Please enter a valid email address"),
    password: z.string().min(6, "Password must be at least 6 characters"),
    confirmPassword: z.string().min(6, "Please confirm your password"),
    // keep required if you want to force it in the UI; backend treats it as optional
    organization_name: z.string().min(2, "Organization name is required"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  });

type SignupFormData = z.infer<typeof signupSchema>;

const fromAxiosError = (error: unknown): string => {
  if (!error) return "Registration failed";
  if (typeof error === "string") return error;
  const axiosError = error as AxiosError<{ detail?: string }>;
  return (
    axiosError.response?.data?.detail ??
    axiosError.message ??
    "Registration failed"
  );
};

const Signup: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = React.useState(false);

  const form = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
      organization_name: "",
    },
  });

  const onSubmit = async (data: SignupFormData) => {
    const { confirmPassword, ...registerData } = data;
    setLoading(true);
    // clear any previous root error
    form.clearErrors("root");

    try {
      await registerUser({
        email: registerData.email,
        name: registerData.name,
        password: registerData.password,
        organization_name: registerData.organization_name, // optional on backend
      });
      navigate("/onboarding"); // or "/login"
    } catch (err: unknown) {
      const msg = fromAxiosError(err);
      // show a visible error in the form
      form.setError("root", { type: "server", message: msg });
      // also log for debugging
      if (typeof err === "object" && err !== null) {
        console.error("Registration failed:", (err as AxiosError).response?.status, msg);
      } else {
        console.error("Registration failed:", msg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-accent/15 via-background to-primary/10">
      <div className="mx-auto flex min-h-screen max-w-5xl items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid w-full gap-10 rounded-3xl border border-border/60 bg-card/95 p-10 shadow-2xl sm:grid-cols-[1.1fr_1fr]">
          <div className="hidden flex-col justify-between rounded-2xl border border-accent/30 bg-accent/20 p-8 text-foreground sm:flex">
            <div className="space-y-4">
              <p className="text-sm font-semibold uppercase tracking-wide text-foreground/70">
                ImpactView onboarding
              </p>
              <h2 className="text-3xl font-semibold leading-snug text-foreground">
                Create your account.
              </h2>
              <p className="text-sm leading-relaxed text-muted-foreground">
                We’ll guide you through upload, mapping, dashboards, and reports with AI co-pilots at every step.
              </p>
            </div>
            <div className="rounded-2xl border border-accent/40 bg-background/80 p-4 text-xs text-muted-foreground">
              Set your organization profile once to power onboarding, data lineage, and PDF exports.
            </div>
          </div>

          <Card className="soft-shadow border-border/60">
            <CardHeader className="space-y-2 text-left">
              <CardTitle className="text-2xl font-semibold text-foreground">Create your account</CardTitle>
              <CardDescription className="text-sm text-muted-foreground">
                Join ImpactView and start tracking equitable, trusted impact.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Full Name</FormLabel>
                        <FormControl>
                          <Input placeholder="Enter your full name" disabled={loading} {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="organization_name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Organization Name</FormLabel>
                        <FormControl>
                          <Input placeholder="Enter your organization name" disabled={loading} {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Email</FormLabel>
                        <FormControl>
                          <Input type="email" placeholder="Enter your email" disabled={loading} {...field} />
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
                          <Input type="password" placeholder="Create a password" disabled={loading} {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="confirmPassword"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Confirm Password</FormLabel>
                        <FormControl>
                          <Input type="password" placeholder="Confirm your password" disabled={loading} {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* Root/server error */}
                  {form.formState.errors.root?.message && (
                    <p className="text-sm text-red-600">{form.formState.errors.root.message}</p>
                  )}

                  <Button type="submit" className="w-full rounded-full bg-primary py-5" disabled={loading}>
                    {loading ? "Creating account..." : "Create Account"}
                  </Button>
                </form>
              </Form>

              <div className="mt-6 text-center">
                <p className="text-sm text-muted-foreground">
                  Already have an account?{" "}
                  <Link to="/login" className="font-medium text-primary hover:text-primary/80">
                    Sign in
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

export default Signup;
