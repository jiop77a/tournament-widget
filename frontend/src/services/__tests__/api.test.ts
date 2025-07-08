import { describe, it, expect, beforeEach, vi } from "vitest";
import { ApiService } from "../api";
import { mockFetch, mockFetchError, mockApiResponses } from "../../test/utils";

describe("ApiService", () => {
  let apiService: ApiService;

  beforeEach(() => {
    apiService = new ApiService("http://localhost:5001/api");
  });

  describe("constructor", () => {
    it("should use provided baseUrl", () => {
      const customApi = new ApiService("https://custom.api.com");
      expect(customApi).toBeInstanceOf(ApiService);
    });

    it("should use environment variable when no baseUrl provided", () => {
      const defaultApi = new ApiService();
      expect(defaultApi).toBeInstanceOf(ApiService);
    });

    it("should fallback to default URL when no baseUrl or env var", () => {
      // Mock import.meta.env to not have VITE_API_BASE_URL
      vi.stubGlobal("import.meta", {
        env: {
          // Exclude VITE_API_BASE_URL to test fallback
          DEV: true,
          PROD: false,
          MODE: "test",
        },
      });

      const fallbackApi = new ApiService();
      expect(fallbackApi).toBeInstanceOf(ApiService);

      // Restore original import.meta
      vi.unstubAllGlobals();
    });
  });

  describe("createTournament", () => {
    it("should create tournament successfully", async () => {
      mockFetch(mockApiResponses.createTournament, 201);

      const result = await apiService.createTournament({
        input_question: "What is the best programming language?",
        custom_prompts: ["Which language is best?"],
        total_prompts: 4,
      });

      expect(fetch).toHaveBeenCalledWith(
        "http://localhost:5001/api/tournament",
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            "Content-Type": "application/json",
          }),
          body: JSON.stringify({
            input_question: "What is the best programming language?",
            custom_prompts: ["Which language is best?"],
            total_prompts: 4,
          }),
        })
      );

      expect(result).toEqual(mockApiResponses.createTournament);
    });

    it("should handle API errors", async () => {
      mockFetchError("Invalid input question", 400);

      await expect(
        apiService.createTournament({
          input_question: "",
          custom_prompts: [],
        })
      ).rejects.toThrow("Invalid input question");
    });
  });

  describe("getTournamentStatus", () => {
    it("should get tournament status successfully", async () => {
      mockFetch(mockApiResponses.tournamentStatus);

      const result = await apiService.getTournamentStatus(1);

      expect(fetch).toHaveBeenCalledWith(
        "http://localhost:5001/api/tournament/1/status",
        expect.objectContaining({
          headers: expect.objectContaining({
            "Content-Type": "application/json",
          }),
        })
      );

      expect(result).toEqual(mockApiResponses.tournamentStatus);
    });

    it("should handle tournament not found", async () => {
      mockFetchError("Tournament not found", 404);

      await expect(apiService.getTournamentStatus(999)).rejects.toThrow(
        "Tournament not found"
      );
    });
  });

  describe("startTournamentBracket", () => {
    it("should start tournament bracket successfully", async () => {
      const mockResponse = {
        message: "Tournament bracket started",
        tournament_id: 1,
        round_1_matches: [
          {
            prompt_1: "Which programming language is the best?",
            prompt_2: "What programming language do you prefer?",
          },
        ],
        total_matches: 1,
      };

      mockFetch(mockResponse, 201);

      const result = await apiService.startTournamentBracket(1);

      expect(fetch).toHaveBeenCalledWith(
        "http://localhost:5001/api/tournament/1/start-bracket",
        expect.objectContaining({
          method: "POST",
        })
      );

      expect(result).toEqual(mockResponse);
    });
  });

  describe("submitMatchResult", () => {
    it("should submit match result successfully", async () => {
      const mockResponse = {
        message: "Match result stored successfully",
        match_id: 1,
        winner: "Which programming language is the best?",
        round_completed: false,
      };

      mockFetch(mockResponse);

      const result = await apiService.submitMatchResult(1, 123);

      expect(fetch).toHaveBeenCalledWith(
        "http://localhost:5001/api/match/1/result",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ winner_id: 123 }),
        })
      );

      expect(result).toEqual(mockResponse);
    });
  });

  describe("error handling", () => {
    it("should handle network errors", async () => {
      global.fetch.mockRejectedValueOnce(new Error("Network error"));

      await expect(apiService.getTournamentStatus(1)).rejects.toThrow(
        "Network error"
      );
    });

    it("should handle non-JSON error responses", async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: "Internal Server Error",
        json: () => Promise.reject(new Error("Not JSON")),
      });

      await expect(apiService.getTournamentStatus(1)).rejects.toThrow(
        "HTTP 500: Internal Server Error"
      );
    });
  });
});
