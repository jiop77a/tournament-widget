import React from "react";
import { useParams, useNavigate } from "react-router-dom";
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
import { useTournament } from "../hooks/useTournament";
import { apiService } from "../services/api";
import type { Match } from "../types";

export const TournamentBracketPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const tournamentId = id ? parseInt(id, 10) : undefined;
  
  const {
    tournament,
    loading,
    error,
    refreshTournament,
    setError,
  } = useTournament(tournamentId);

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
      navigate(`/tournament/${tournament.tournament_id}/match/${match.match_id}`);
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
