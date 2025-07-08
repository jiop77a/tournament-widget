import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "../../test/utils";
import { TournamentCreationForm } from "../TournamentCreationForm";

// Mock the API service
vi.mock("../../services/api", () => ({
  apiService: {
    createTournament: vi.fn(),
  },
}));

describe("TournamentCreationForm", () => {
  const mockOnTournamentCreated = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should render form elements", () => {
    render(
      <TournamentCreationForm onTournamentCreated={mockOnTournamentCreated} />
    );

    expect(screen.getByLabelText(/tournament question/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/total prompts/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /create tournament/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /add another prompt/i })
    ).toBeInTheDocument();
  });

  it("should have a disabled delete button when only one prompt exists", () => {
    render(
      <TournamentCreationForm onTournamentCreated={mockOnTournamentCreated} />
    );

    const deleteButton = screen.getByLabelText(/delete prompt 1/i);
    expect(deleteButton).toBeDisabled();
  });
});
