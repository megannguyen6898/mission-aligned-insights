import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { PageHeader } from "@/components/layout/PageHeader";
import { useAuth } from "../contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";
import { Badge } from "@/components/ui/badge";
import { ShieldCheck, Sparkles } from "lucide-react";

const settingsSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  organization_name: z.string().min(2, "Organization name is required"),
  mission: z.string().optional(),
  audience: z.string().optional(),
  sector: z.string().optional(),
  region: z.string().optional(),
  organization_size: z.string().optional(),
  key_goals: z.string().optional(),
});

type SettingsFormData = z.infer<typeof settingsSchema>;

const Settings: React.FC = () => {
  const { user } = useAuth();
  const { toast } = useToast();

  const form = useForm<SettingsFormData>({
    resolver: zodResolver(settingsSchema),
    defaultValues: {
      name: user?.name || "",
      organization_name: user?.organization_name || "",
      mission: user?.mission || "",
      audience: user?.audience || "",
      sector: user?.sector || "",
      region: user?.region || "",
      organization_size: user?.organization_size || "",
      key_goals: user?.key_goals || "",
    },
  });

  const onSubmit = async (data: SettingsFormData) => {
    try {
      // Hook up to API when ready
      toast({
        title: "Settings updated",
        description: "Your profile fuels impact narratives, dashboards, and exports.",
      });
    } catch (error) {
      toast({
        title: "Update failed",
        description: "Please try again",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-10">
      <PageHeader
        title="Organization settings"
        description="Keep your profile aligned with board-ready narratives. These details flow through upload lineage, dashboards, and every exported report."
      />

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_320px]">
        <Card className="rounded-2xl border-border/60 bg-card/95 soft-shadow">
          <CardHeader>
            <CardTitle className="text-lg font-semibold text-foreground">Profile & preferences</CardTitle>
            <CardDescription className="text-sm leading-relaxed text-muted-foreground">
              Update the information stakeholders see across dashboards, AI narratives, and PDF exports.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
                <div className="grid gap-6 md:grid-cols-2">
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Full name</FormLabel>
                        <FormControl>
                          <Input {...field} placeholder="Amara Singh" />
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
                        <FormLabel>Organization</FormLabel>
                        <FormControl>
                          <Input {...field} placeholder="Impact Collective" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <FormField
                  control={form.control}
                  name="mission"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Mission statement</FormLabel>
                      <FormControl>
                        <Textarea
                          {...field}
                          rows={4}
                          placeholder="Share how your programs deliver measurable, equitable impact."
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="grid gap-6 md:grid-cols-2">
                  <FormField
                    control={form.control}
                    name="audience"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Stakeholder audience</FormLabel>
                        <FormControl>
                          <Input {...field} placeholder="Board, programme leads, funders" />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="sector"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Primary sector</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select sector" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="education">Education</SelectItem>
                            <SelectItem value="healthcare">Healthcare</SelectItem>
                            <SelectItem value="environment">Environment</SelectItem>
                            <SelectItem value="poverty">Poverty alleviation</SelectItem>
                            <SelectItem value="social-enterprise">Social enterprise</SelectItem>
                            <SelectItem value="other">Other</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <div className="grid gap-6 md:grid-cols-3">
                  <FormField
                    control={form.control}
                    name="region"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Region</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select region" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="north-america">North America</SelectItem>
                            <SelectItem value="europe">Europe</SelectItem>
                            <SelectItem value="asia-pacific">Asia Pacific</SelectItem>
                            <SelectItem value="africa">Africa</SelectItem>
                            <SelectItem value="latin-america">Latin America</SelectItem>
                            <SelectItem value="global">Global</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="organization_size"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Org size</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select size" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="small">1-10</SelectItem>
                            <SelectItem value="medium">11-100</SelectItem>
                            <SelectItem value="large">101-500</SelectItem>
                            <SelectItem value="enterprise">500+</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="key_goals"
                    render={({ field }) => (
                      <FormItem className="md:col-span-1 md:col-start-3">
                        <FormLabel>Key goals</FormLabel>
                        <FormControl>
                          <Textarea
                            {...field}
                            rows={3}
                            placeholder="Highlight up to three outcomes you are driving this year."
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <div className="flex justify-end">
                  <Button type="submit" className="rounded-full bg-primary px-6">
                    Save changes
                  </Button>
                </div>
              </form>
            </Form>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card className="rounded-2xl border-border/60 bg-card soft-shadow">
            <CardHeader>
              <CardTitle className="text-base font-semibold text-foreground">Trust & governance</CardTitle>
              <CardDescription className="text-sm text-muted-foreground leading-relaxed">
                Settings flow into audit logs, AI narratives, and export metadata.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-muted-foreground">
              <div className="flex items-start gap-3 rounded-2xl border border-primary/20 bg-primary/10 p-4 text-primary">
                <ShieldCheck className="mt-0.5 h-4 w-4" />
                <p className="leading-relaxed">
                  Changes are timestamped and linked to ingestion batches. Review audit history under Impact → Audit trail.
                </p>
              </div>
              <div className="flex items-start gap-3 rounded-2xl border border-border/50 bg-muted/30 p-4">
                <Sparkles className="mt-0.5 h-4 w-4 text-muted-foreground" />
                <p className="leading-relaxed">
                  AI narratives incorporate your mission and key goals to stay human and contextual.
                </p>
              </div>
              <Badge variant="secondary" className="rounded-full bg-primary/10 text-primary">
                WCAG AA compliant
              </Badge>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Settings;
