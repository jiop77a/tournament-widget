// Mock utilities for API testing

// Helper to mock fetch responses
export const mockFetch = (response: unknown, status = 200) => {
  global.fetch.mockResolvedValueOnce({
    ok: status >= 200 && status < 300,
    status,
    json: async () => response,
  });
};

// Helper to mock fetch errors
export const mockFetchError = (error: string, status = 500) => {
  global.fetch.mockResolvedValueOnce({
    ok: false,
    status,
    json: async () => ({ error }),
  });
};

// Mock API responses
export const mockApiResponses = {
  createTournament: {
    tournament_id: 1,
    input_question: "What is the best programming language?",
    prompts: [
      "Which programming language is the best?",
      "What programming language do you prefer?",
      "Tell me the top programming language",
      "What is your favorite programming language?",
    ],
  },
  tournamentStatus: {
    tournament_id: 1,
    input_question: "What is the best programming language?",
    status: "in_progress",
    current_round: 1,
    total_prompts: 4,
    progress: {
      total_matches: 2,
      completed_matches: 0,
      completion_percentage: 0.0,
    },
    rounds: {
      "1": [
        {
          match_id: 1,
          prompt_1: "Which programming language is the best?",
          prompt_2: "What programming language do you prefer?",
          status: "pending",
          winner: null,
        },
        {
          match_id: 2,
          prompt_1: "Tell me the top programming language",
          prompt_2: "What is your favorite programming language?",
          status: "pending",
          winner: null,
        },
      ],
    },
    winner: null,
  },
  startBracket: {
    message: "Tournament bracket started successfully",
    current_round: 1,
    matches: [
      {
        match_id: 1,
        round: 1,
        prompt_1: "Python",
        prompt_2: "JavaScript",
        status: "pending",
        winner: null,
      },
    ],
  },
  submitResult: {
    message: "Match result submitted successfully",
    match: {
      match_id: 1,
      round: 1,
      prompt_1: "Python",
      prompt_2: "JavaScript",
      status: "completed",
      winner: "Python",
    },
    next_round_created: false,
    tournament_complete: false,
    winner: null,
  },
};
