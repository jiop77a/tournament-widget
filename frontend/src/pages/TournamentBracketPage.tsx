import React, { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import {
  Box,
  Button,
  Alert,
  CircularProgress,
  Typography,
} from "@mui/material";
import { Add as CreateIcon, Refresh as RefreshIcon } from "@mui/icons-material";
import { NavigationHeader } from "../components/NavigationHeader";
import { TournamentBracket } from "../components/TournamentBracket";
import { ShareTournament } from "../components/ShareTournament";
import { MatchResultBanners } from "../components/MatchResultBanners";
import { useTournament } from "../hooks/useTournament";
import { apiService } from "../services/api";
import type { Match } from "../types";
import type { SubmitMatchResultResponse } from "../types/api";

export const TournamentBracketPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  const tournamentId = id ? parseInt(id, 10) : undefined;

  const { tournament, loading, error, refreshTournament, setError } =
    useTournament(tournamentId);

  // State for match result banners
  const [matchResult, setMatchResult] =
    useState<SubmitMatchResultResponse | null>(null);

  // Handle match result from navigation state
  useEffect(() => {
    if (location.state?.matchResult) {
      setMatchResult(location.state.matchResult);

      // Clear the navigation state to prevent showing banners on refresh
      navigate(location.pathname, { replace: true });
    }
  }, [location.state, navigate, location.pathname]);

  if (!tournamentId || isNaN(tournamentId)) {
    return (
      <Box>
        <NavigationHeader />
        <Alert severity="error">
          Invalid tournament ID. Please check the URL and try again.
        </Alert>
      </Box>
    );
  }

  const handleMatchClick = (match: Match) => {
    if (match.status === "pending" && tournament) {
      // Navigate to the match voting URL
      navigate(
        `/tournament/${tournament.tournament_id}/match/${match.match_id}`
      );
    }
  };

  const handleStartBracket = async () => {
    if (!tournament) return;

    try {
      await apiService.startTournamentBracket(tournament.tournament_id);
      await refreshTournament();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to start tournament bracket"
      );
    }
  };

  const handleCreateNew = () => {
    navigate("/");
  };

  if (loading && !tournament) {
    return (
      <Box>
        <NavigationHeader tournamentId={tournamentId} />
        <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
          <CircularProgress />
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      <NavigationHeader tournamentId={tournamentId} />

      <Typography variant="h2" component="h1" gutterBottom textAlign="center">
        Tournament #{tournamentId}
      </Typography>

      {/* Match Result Banners */}
      <MatchResultBanners
        key={matchResult?.match_id}
        matchResult={matchResult}
      />

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
          variant="outlined"
          startIcon={<CreateIcon />}
          onClick={handleCreateNew}
          disabled={loading}
        >
          Create New Tournament
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

        {tournament && (
          <ShareTournament tournamentId={tournament.tournament_id} compact />
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {tournament && (
        <TournamentBracket
          tournament={tournament}
          onMatchClick={handleMatchClick}
          onStartBracket={handleStartBracket}
        />
      )}
    </Box>
  );
};
