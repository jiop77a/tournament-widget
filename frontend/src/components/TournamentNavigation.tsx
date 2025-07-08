import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Button,
  Alert,
  CircularProgress,
  Typography,
  Card,
  CardContent,
} from "@mui/material";
import { Add as CreateIcon, Refresh as RefreshIcon } from "@mui/icons-material";
import { apiService } from "../services/api";
import { TournamentCreationForm } from "./TournamentCreationForm";
import { TournamentBracket } from "./TournamentBracket";
import { MatchVoting } from "./MatchVoting";
import type { CreateTournamentResponse, Tournament, Match } from "../types";

type ViewMode = "create" | "bracket" | "voting";

interface TournamentNavigationProps {
  initialTournamentId?: number;
  initialMatchId?: number;
}

export const TournamentNavigation: React.FC<TournamentNavigationProps> = ({
  initialTournamentId,
  initialMatchId,
}) => {
  const navigate = useNavigate();
  const [viewMode, setViewMode] = useState<ViewMode>("create");
  const [currentTournament, setCurrentTournament] = useState<Tournament | null>(
    null
  );
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pollingEnabled, setPollingEnabled] = useState(false);

  // Polling effect for tournament updates
  useEffect(() => {
    if (
      !pollingEnabled ||
      !currentTournament ||
      currentTournament.status === "completed"
    ) {
      return;
    }

    const pollInterval = setInterval(async () => {
      try {
        const updatedTournament = await apiService.getTournamentStatus(
          currentTournament.tournament_id
        );
        setCurrentTournament(updatedTournament);

        // Stop polling if tournament is completed
        if (updatedTournament.status === "completed") {
          setPollingEnabled(false);
        }
      } catch (err) {
        console.error("Polling error:", err);
        // Don't show error for polling failures to avoid spam
      }
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(pollInterval);
  }, [pollingEnabled, currentTournament]);

  const loadTournament = useCallback(async (tournamentId: number) => {
    setLoading(true);
    setError(null);

    try {
      const tournament = await apiService.getTournamentStatus(tournamentId);
      setCurrentTournament(tournament);
      setViewMode("bracket");

      // Tournament loaded successfully - prompts are now included in the tournament object

      // Enable polling for active tournaments
      if (tournament.status === "in_progress") {
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

  // Load tournament if initial ID is provided
  useEffect(() => {
    if (initialTournamentId) {
      loadTournament(initialTournamentId);
    }
  }, [initialTournamentId, loadTournament]);

  // Handle initial match ID for direct match voting links
  useEffect(() => {
    if (initialMatchId && currentTournament) {
      // Find the match in the tournament rounds
      const allMatches = Object.values(currentTournament.rounds).flat();
      const match = allMatches.find((m) => m.match_id === initialMatchId);

      if (match && match.status === "pending") {
        setSelectedMatch(match);
        setViewMode("voting");
      }
    }
  }, [initialMatchId, currentTournament]);

  const refreshTournament = async () => {
    if (!currentTournament) return;
    await loadTournament(currentTournament.tournament_id);
  };

  const handleTournamentCreated = (tournament: CreateTournamentResponse) => {
    // Navigate to the new tournament page
    navigate(`/tournament/${tournament.tournament_id}`);
    // Load the full tournament data (which now includes prompts)
    loadTournament(tournament.tournament_id);
  };

  const handleStartBracket = async () => {
    if (!currentTournament) return;

    setLoading(true);
    setError(null);

    try {
      await apiService.startTournamentBracket(currentTournament.tournament_id);

      // Refresh tournament data to show the bracket
      await refreshTournament();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to start tournament bracket"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleMatchClick = (match: Match) => {
    if (match.status === "pending" && currentTournament) {
      // Navigate to the match voting URL
      navigate(
        `/tournament/${currentTournament.tournament_id}/match/${match.match_id}`
      );
      setSelectedMatch(match);
      setViewMode("voting");
    }
  };

  const handleVoteSubmitted = async () => {
    // Refresh tournament data to reflect the new results
    await refreshTournament();

    // Navigate back to tournament page
    if (currentTournament) {
      navigate(`/tournament/${currentTournament.tournament_id}`);
    }

    // If tournament is completed, stay on bracket view to show winner
    // Otherwise, go back to bracket view
    setViewMode("bracket");
    setSelectedMatch(null);
  };

  const handleBackToBracket = () => {
    // Navigate back to tournament page
    if (currentTournament) {
      navigate(`/tournament/${currentTournament.tournament_id}`);
    }
    setViewMode("bracket");
    setSelectedMatch(null);
  };

  const handleCreateNew = () => {
    setCurrentTournament(null);
    setSelectedMatch(null);
    setViewMode("create");
    setError(null);
    setPollingEnabled(false);
  };

  if (loading && !currentTournament) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Navigation Header */}
      <Box
        sx={{
          mb: 3,
          display: "flex",
          gap: 2,
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <Button
          variant={viewMode === "create" ? "contained" : "outlined"}
          startIcon={<CreateIcon />}
          onClick={handleCreateNew}
          disabled={loading}
        >
          Create Tournament
        </Button>

        {currentTournament && (
          <>
            <Button
              variant={viewMode === "bracket" ? "contained" : "outlined"}
              onClick={() => setViewMode("bracket")}
              disabled={loading}
            >
              View Bracket
            </Button>

            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={refreshTournament}
              disabled={loading}
              size="small"
            >
              {loading ? "Refreshing..." : "Refresh"}
            </Button>
          </>
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Content based on view mode */}
      {viewMode === "create" && (
        <TournamentCreationForm onTournamentCreated={handleTournamentCreated} />
      )}

      {viewMode === "bracket" && currentTournament && (
        <TournamentBracket
          tournament={currentTournament}
          onMatchClick={handleMatchClick}
          onStartBracket={handleStartBracket}
        />
      )}

      {viewMode === "voting" && selectedMatch && (
        <MatchVoting
          match={selectedMatch}
          onVoteSubmitted={handleVoteSubmitted}
          onBack={handleBackToBracket}
        />
      )}

      {/* Tournament Info Footer */}
      {currentTournament && viewMode !== "create" && (
        <Card sx={{ mt: 3, backgroundColor: "grey.50" }}>
          <CardContent>
            <Typography variant="caption" color="text.secondary">
              Tournament #{currentTournament.tournament_id} •{" "}
              {currentTournament.status} • Round{" "}
              {currentTournament.current_round} •
              {currentTournament.progress.completion_percentage}% complete
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};
