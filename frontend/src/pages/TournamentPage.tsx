import React from "react";
import { useParams } from "react-router-dom";
import { Box, Typography, Alert } from "@mui/material";
import { TournamentNavigation } from "../components/TournamentNavigation";
import { NavigationHeader } from "../components/NavigationHeader";

export const TournamentPage: React.FC = () => {
  const { id, matchId } = useParams<{ id: string; matchId?: string }>();

  const tournamentId = id ? parseInt(id, 10) : undefined;
  const matchIdNum = matchId ? parseInt(matchId, 10) : undefined;

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

  return (
    <Box>
      <NavigationHeader tournamentId={tournamentId} matchId={matchIdNum} />

      <Typography variant="h2" component="h1" gutterBottom textAlign="center">
        Tournament #{tournamentId}
      </Typography>

      <TournamentNavigation
        initialTournamentId={tournamentId}
        initialMatchId={matchIdNum}
      />
    </Box>
  );
};
