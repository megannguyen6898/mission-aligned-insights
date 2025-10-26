import { render, screen } from "@testing-library/react";
import Dashboard from "@/pages/Dashboard";

describe("Dashboard page", () => {
  it("shows KPI cards and AI narrative summary", () => {
    render(<Dashboard />);

    expect(screen.getByRole("heading", { name: /impact intelligence/i })).toBeInTheDocument();
    expect(screen.getByText(/AI narrative/i)).toBeInTheDocument();
    expect(screen.getByText(/Lives impacted/i)).toBeInTheDocument();
  });
});
