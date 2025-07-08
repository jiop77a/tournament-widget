import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Alert,
  CircularProgress,
  Typography,
} from "@mui/material";
import { NavigationHeader } from "../components/NavigationHeader";
import { MatchVoting } from "../components/MatchVoting";
import { useTournament } from "../hooks/useTournament";
import type { Match } from "../types";

export const MatchVotingPage: React.FC = () => {
  const { id, matchId } = useParams<{ id: string; matchId: string }>();
  const navigate = useNavigate();
  
  const tournamentId = id ? parseInt(id, 10) : undefined;
  const matchIdNum = matchId ? parseInt(matchId, 10) : undefined;
  
  const [selectedMatch, setSelectedMatch] = useState<Match | null>(null);
  
  const {
    tournament,
    loading,
    error,
    refreshTournament,
    setError,
  } = useTournament(tournamentId);

  // Handle match validation and selection
  useEffect(() => {
    if (matchIdNum && tournament) {
      // Find the match in the tournament rounds
      const allMatches = Object.values(tournament.rounds).flat();
      const match = allMatches.find((m) => m.match_id === matchIdNum);

      if (match && match.status === "pending") {
        setSelectedMatch(match);
      } else {
        // Match doesn't exist or is not pending - redirect to tournament page with message
        let message = "";
        if (!match) {
          message = `Match #${matchIdNum} not found in this tournament.`;
        } else if (match.status === "completed") {
          message = `Match #${matchIdNum} has already been completed.`;
        } else {
          message = `Match #${matchIdNum} is not available for voting.`;
        }

        // Update URL to tournament page and show temporary message
        navigate(`/tournament/${tournament.tournament_id}`, {
          replace: true,
        });
        setError(message);

        // Clear the error message after 5 seconds
        setTimeout(() => setError(null), 5000);
      }
    }
  }, [matchIdNum, tournament, navigate, setError]);

  if (!tournamentId || isNaN(tournamentId) || !matchIdNum || isNaN(matchIdNum)) {
    return (
      <Box>
        <NavigationHeader />
        <Alert severity="error">
          Invalid tournament or match ID. Please check the URL and try again.
        </Alert>
      </Box>
    );
  }

  const handleVoteSubmitted = async () => {
    // Navigate back to tournament page
    if (tournament) {
      navigate(`/tournament/${tournament.tournament_id}`);
    }

    // Refresh tournament data to reflect the new results
    await refreshTournament();
  };

  const handleBackToBracket = () => {
    // Navigate back to tournament page
    if (tournament) {
      navigate(`/tournament/${tournament.tournament_id}`);
    }
  };

  if (loading && !tournament) {
    return (
      <Box>
        <NavigationHeader tournamentId={tournamentId} matchId={matchIdNum} />
        <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
          <CircularProgress />
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      <NavigationHeader tournamentId={tournamentId} matchId={matchIdNum} />

      <Typography variant="h2" component="h1" gutterBottom textAlign="center">
        Tournament #{tournamentId}
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {selectedMatch && (
        <MatchVoting
          match={selectedMatch}
          onVoteSubmitted={handleVoteSubmitted}
          onBack={handleBackToBracket}
        />
      )}
    </Box>
  );
};
