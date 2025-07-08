import {
  Container,
  Box,
  ThemeProvider,
  createTheme,
  CssBaseline,
} from "@mui/material";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { TournamentPage } from "./pages/TournamentPage";
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
              <Route path="/tournament/:id" element={<TournamentPage />} />
              <Route
                path="/tournament/:id/match/:matchId"
                element={<TournamentPage />}
              />
            </Routes>
          </Box>
        </Container>
      </Router>
    </ThemeProvider>
  );
}

export default App;
