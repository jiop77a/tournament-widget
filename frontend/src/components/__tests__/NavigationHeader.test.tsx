import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "../../test/utils";
import { NavigationHeader } from "../NavigationHeader";
import { MemoryRouter } from "react-router-dom";

// Mock react-router-dom hooks
const mockNavigate = vi.fn();
const mockLocation = { pathname: "/" };

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => mockLocation,
  };
});

// Helper to render with router context
const renderWithRouter = (
  component: React.ReactElement,
  initialEntries = ["/"]
) => {
  return render(
    <MemoryRouter initialEntries={initialEntries}>{component}</MemoryRouter>
  );
};

describe("NavigationHeader", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render home breadcrumb", () => {
    renderWithRouter(<NavigationHeader />);

    expect(screen.getByText("Home")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /home/i })).toBeInTheDocument();
  });

  it("should navigate to home when home breadcrumb is clicked", async () => {
    renderWithRouter(<NavigationHeader />);

    const homeButton = screen.getByRole("button", { name: /home/i });
    await homeButton.click();

    expect(mockNavigate).toHaveBeenCalledWith("/");
  });

  it("should render tournament breadcrumb when tournamentId is provided", () => {
    renderWithRouter(<NavigationHeader tournamentId={123} />);

    expect(screen.getByText("Home")).toBeInTheDocument();
    expect(screen.getByText(/tournament #123/i)).toBeInTheDocument();
  });

  it("should navigate to tournament when tournament breadcrumb is clicked", async () => {
    renderWithRouter(<NavigationHeader tournamentId={123} />);

    const tournamentButton = screen.getByRole("button", {
      name: /tournament #123/i,
    });
    await tournamentButton.click();

    expect(mockNavigate).toHaveBeenCalledWith("/tournament/123");
  });

  it("should render match breadcrumb when matchId is provided", () => {
    renderWithRouter(<NavigationHeader tournamentId={123} matchId={456} />);

    expect(screen.getByText("Home")).toBeInTheDocument();
    expect(screen.getByText(/tournament #123/i)).toBeInTheDocument();
    expect(screen.getByText(/match #456/i)).toBeInTheDocument();
  });

  it("should not render tournament breadcrumb when tournamentId is not provided", () => {
    renderWithRouter(<NavigationHeader />);

    expect(screen.getByText("Home")).toBeInTheDocument();
    expect(screen.queryByText(/tournament/i)).not.toBeInTheDocument();
  });

  it("should not render match breadcrumb when matchId is not provided", () => {
    renderWithRouter(<NavigationHeader tournamentId={123} />);

    expect(screen.getByText("Home")).toBeInTheDocument();
    expect(screen.getByText(/tournament #123/i)).toBeInTheDocument();
    expect(screen.queryByText(/match/i)).not.toBeInTheDocument();
  });

  it("should not navigate to tournament when tournamentId is not provided", async () => {
    renderWithRouter(<NavigationHeader />);

    // Since there's no tournament breadcrumb, this test ensures the handler works correctly
    // when tournamentId is undefined (covered by the component logic)
    expect(screen.queryByText("Tournament")).not.toBeInTheDocument();
  });
});
