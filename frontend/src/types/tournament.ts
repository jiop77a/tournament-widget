// Tournament-related type definitions

export interface Tournament {
  tournament_id: number;
  input_question: string;
  status: string;
  current_round: number;
  total_prompts: number;
  prompts: string[];
  progress: {
    total_matches: number;
    completed_matches: number;
    completion_percentage: number;
  };
  rounds: Record<string, Match[]>;
  byes: Record<string, string[]>;
  winner: string | null;
}

export interface Match {
  match_id: number;
  prompt_1: string;
  prompt_2: string;
  prompt_1_id: number;
  prompt_2_id: number;
  status: string;
  winner: string | null;
  round_number?: number;
}
