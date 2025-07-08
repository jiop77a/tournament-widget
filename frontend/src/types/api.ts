// API request and response type definitions

export interface CreateTournamentRequest {
  input_question: string;
  custom_prompts: string[];
  total_prompts?: number;
}

export interface CreateTournamentResponse {
  tournament_id: number;
  input_question: string;
  prompts: string[];
}

export interface StartTournamentBracketResponse {
  message: string;
  tournament_id: number;
  round_1_matches: Array<{ prompt_1: string; prompt_2: string }>;
  total_matches: number;
}

export interface SubmitMatchResultResponse {
  message: string;
  match_id: number;
  winner: string;
  round_completed: boolean;
  next_round?: number;
  next_round_matches?: Array<{ prompt_1: string; prompt_2: string }>;
  tournament_completed?: boolean;
  tournament_winner?: string;
}

export interface GetTournamentMatchesResponse {
  tournament_id: number;
  matches: import('./tournament').Match[];
  total_matches: number;
}

export interface Prompt {
  id: number;
  text: string;
}
