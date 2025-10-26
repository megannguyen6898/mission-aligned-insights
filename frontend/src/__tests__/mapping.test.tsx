import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Mapping from "@/pages/Mapping";

describe("Mapping page", () => {
  it("renders workflow guidance and toggles advanced mapping preview", async () => {
    render(<Mapping />);

    expect(
      screen.getByRole("heading", { name: /confirm smart mappings/i })
    ).toBeInTheDocument();

    expect(
      screen.queryByText(/advanced mapping preview/i)
    ).not.toBeInTheDocument();

    await userEvent.click(screen.getByLabelText(/advanced mapping toggle/i));

    expect(
      screen.getByText(/advanced mapping preview/i)
    ).toBeInTheDocument();
  });
});
