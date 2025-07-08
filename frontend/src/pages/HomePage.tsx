import React from "react";
import { useNavigate } from "react-router-dom";
import { Box, Typography } from "@mui/material";
import { TournamentCreationForm } from "../components/TournamentCreationForm";
import { NavigationHeader } from "../components/NavigationHeader";
import type { CreateTournamentResponse } from "../types";

export const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const handleTournamentCreated = (response: CreateTournamentResponse) => {
    // Navigate to the new tournament's bracket page
    navigate(`/tournament/${response.tournament_id}`);
  };

  return (
    <Box>
      <NavigationHeader />

      <Typography variant="h2" component="h1" gutterBottom textAlign="center">
        Tournament Widget
      </Typography>
      <Typography
        variant="h5"
        component="h2"
        gutterBottom
        color="text.secondary"
        textAlign="center"
        sx={{ mb: 4 }}
      >
        Create and manage prompt tournaments
      </Typography>

      <TournamentCreationForm onTournamentCreated={handleTournamentCreated} />
    </Box>
  );
};
