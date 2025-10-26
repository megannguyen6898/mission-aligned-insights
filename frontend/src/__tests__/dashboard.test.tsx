import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import Dashboard from "@/pages/Dashboard";

vi.mock("@/lib/apiClient", () => ({
  getKpis: vi.fn().mockResolvedValue({
    kpis: [
      { label: "Beneficiaries", value: 2500, delta: 0.12, unit: "people" },
      { label: "Spend", value: 182000, delta: 0.06, unit: "USD" },
    ],
  }),
  getSeries: vi.fn().mockResolvedValue({
    series: [
      {
        label: "Beneficiaries",
        points: [
          { x: 2021, y: 520 },
          { x: 2022, y: 640 },
        ],
      },
      {
        label: "Completions",
        points: [
          { x: 2021, y: 410 },
          { x: 2022, y: 495 },
        ],
      },
    ],
    meta: { unit: "people" },
  }),
  renderReport: vi.fn(),
}));

vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({ user: { organization_name: "org1", name: "Test User" } }),
}));

describe("Dashboard page", () => {
  it("shows KPI cards and AI narrative summary", async () => {
    const queryClient = new QueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <Dashboard />
      </QueryClientProvider>
    );

    expect(await screen.findByRole("heading", { name: /impact intelligence/i })).toBeInTheDocument();
    expect(await screen.findByText(/AI narrative/i)).toBeInTheDocument();
    expect(await screen.findByText(/Beneficiaries/)).toBeInTheDocument();
  });
});
