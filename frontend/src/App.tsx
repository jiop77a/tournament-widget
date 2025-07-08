import {
  Container,
  Typography,
  Box,
  ThemeProvider,
  createTheme,
  CssBaseline,
} from "@mui/material";
import { TournamentNavigation } from "./components/TournamentNavigation";

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
      <Container maxWidth="lg">
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

          <TournamentNavigation />
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
