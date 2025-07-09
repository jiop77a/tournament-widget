// API service for tournament backend communication

import type {
  Tournament,
  CreateTournamentRequest,
  CreateTournamentResponse,
  StartTournamentBracketResponse,
  SubmitMatchResultResponse,
  GetTournamentMatchesResponse,
  Prompt,
} from "../types";

class ApiService {
  private baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl =
      baseUrl ||
      import.meta.env.VITE_API_BASE_URL ||
      "http://localhost:5001/api";
  }
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const config: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.error || `HTTP ${response.status}: ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error("An unexpected error occurred");
    }
  }

  // Create a new tournament
  async createTournament(
    data: CreateTournamentRequest
  ): Promise<CreateTournamentResponse> {
    return this.request<CreateTournamentResponse>("/tournament", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Get tournament status
  async getTournamentStatus(tournamentId: number): Promise<Tournament> {
    return this.request<Tournament>(`/tournament/${tournamentId}/status`);
  }

  // Start tournament bracket
  async startTournamentBracket(
    tournamentId: number
  ): Promise<StartTournamentBracketResponse> {
    return this.request(`/tournament/${tournamentId}/start-bracket`, {
      method: "POST",
    });
  }

  // Submit match result
  async submitMatchResult(
    matchId: number,
    winnerId: number
  ): Promise<SubmitMatchResultResponse> {
    return this.request(`/match/${matchId}/result`, {
      method: "POST",
      body: JSON.stringify({ winner_id: winnerId }),
    });
  }

  // Get tournament matches
  async getTournamentMatches(
    tournamentId: number,
    round?: number
  ): Promise<GetTournamentMatchesResponse> {
    const endpoint = round
      ? `/tournament/${tournamentId}/matches?round=${round}`
      : `/tournament/${tournamentId}/matches`;

    return this.request(endpoint);
  }

  // Get all prompts (utility)
  async getAllPrompts(): Promise<Prompt[]> {
    return this.request("/prompts");
  }

  // Check if OpenAI is available
  async getOpenAIStatus(): Promise<{ available: boolean }> {
    return this.request("/openai-status");
  }

  // Test a prompt with AI
  async testPrompt(data: {
    prompt: string;
    model?: string;
    max_tokens?: number;
    temperature?: number;
  }): Promise<{
    prompt: string;
    response: string;
    model: string;
    max_tokens: number;
    temperature: number;
    usage: {
      prompt_tokens: number;
      completion_tokens: number;
      total_tokens: number;
    };
  }> {
    return this.request("/test-prompt", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }
}

// Export the class for custom instantiation
export { ApiService };

// Export a default instance using environment configuration
export const apiService = new ApiService();
