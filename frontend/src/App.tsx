import { useState } from "react";
import {
  Container,
  Typography,
  Box,
  ThemeProvider,
  createTheme,
  CssBaseline,
} from "@mui/material";
import { TournamentCreationForm } from "./components/TournamentCreationForm";
import type { CreateTournamentResponse } from "./types";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1976d2",
    },
  },
});

function App() {
  const [createdTournament, setCreatedTournament] =
    useState<CreateTournamentResponse | null>(null);

  const handleTournamentCreated = (tournament: CreateTournamentResponse) => {
    setCreatedTournament(tournament);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="md">
        <Box sx={{ my: 4 }}>
          <Typography
            variant="h2"
            component="h1"
            gutterBottom
            textAlign="center"
          >
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

          <TournamentCreationForm
            onTournamentCreated={handleTournamentCreated}
          />

          {createdTournament && (
            <Box sx={{ mt: 3, textAlign: "center" }}>
              <Typography variant="h6" color="success.main">
                Tournament #{createdTournament.tournament_id} created
                successfully!
              </Typography>
            </Box>
          )}
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
