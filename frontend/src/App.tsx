import {
  Container,
  Box,
  ThemeProvider,
  createTheme,
  CssBaseline,
} from "@mui/material";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { TournamentBracketPage } from "./pages/TournamentBracketPage";
import { MatchVotingPage } from "./pages/MatchVotingPage";
import { HomePage } from "./pages/HomePage";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1976d2",
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Container maxWidth="lg">
          <Box sx={{ my: 4 }}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route
                path="/tournament/:id"
                element={<TournamentBracketPage />}
              />
              <Route
                path="/tournament/:id/match/:matchId"
                element={<MatchVotingPage />}
              />
            </Routes>
          </Box>
        </Container>
      </Router>
    </ThemeProvider>
  );
}

export default App;
