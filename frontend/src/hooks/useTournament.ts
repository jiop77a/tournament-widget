import { useState, useEffect, useCallback } from "react";
import { apiService } from "../services/api";
import type { Tournament } from "../types";

interface UseTournamentResult {
  tournament: Tournament | null;
  loading: boolean;
  error: string | null;
  pollingEnabled: boolean;
  loadTournament: (tournamentId: number) => Promise<void>;
  refreshTournament: () => Promise<void>;
  setError: (error: string | null) => void;
  setPollingEnabled: (enabled: boolean) => void;
}

export const useTournament = (initialTournamentId?: number): UseTournamentResult => {
  const [tournament, setTournament] = useState<Tournament | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pollingEnabled, setPollingEnabled] = useState(false);

  const loadTournament = useCallback(async (tournamentId: number) => {
    setLoading(true);
    setError(null);

    try {
      const tournamentData = await apiService.getTournamentStatus(tournamentId);
      setTournament(tournamentData);

      // Enable polling for active tournaments
      if (tournamentData.status === "in_progress") {
        setPollingEnabled(true);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load tournament"
      );
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshTournament = useCallback(async () => {
    if (!tournament) return;
    await loadTournament(tournament.tournament_id);
  }, [tournament, loadTournament]);

  // Load tournament if initial ID is provided
  useEffect(() => {
    if (initialTournamentId) {
      loadTournament(initialTournamentId);
    }
  }, [initialTournamentId, loadTournament]);

  // Polling effect for tournament updates
  useEffect(() => {
    if (
      pollingEnabled &&
      tournament &&
      tournament.status === "in_progress"
    ) {
      const interval = setInterval(() => {
        refreshTournament();
      }, 5000); // Poll every 5 seconds

      return () => clearInterval(interval);
    }
  }, [pollingEnabled, tournament, refreshTournament]);

  return {
    tournament,
    loading,
    error,
    pollingEnabled,
    loadTournament,
    refreshTournament,
    setError,
    setPollingEnabled,
  };
};
