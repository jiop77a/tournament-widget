// Tournament-related type definitions

export interface Tournament {
  tournament_id: number;
  input_question: string;
  status: string;
  current_round: number;
  total_prompts: number;
  progress: {
    total_matches: number;
    completed_matches: number;
    completion_percentage: number;
  };
  rounds: Record<string, Match[]>;
  winner: string | null;
}

export interface Match {
  match_id: number;
  prompt_1: string;
  prompt_2: string;
  status: string;
  winner: string | null;
  round_number?: number;
}
