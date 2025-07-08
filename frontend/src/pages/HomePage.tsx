import React from "react";
import { Box, Typography } from "@mui/material";
import { TournamentNavigation } from "../components/TournamentNavigation";
import { NavigationHeader } from "../components/NavigationHeader";

export const HomePage: React.FC = () => {
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

      <TournamentNavigation />
    </Box>
  );
};
