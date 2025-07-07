import { useState } from "react";
import {
  Container,
  Typography,
  Button,
  Box,
  Card,
  CardContent,
  ThemeProvider,
  createTheme,
  CssBaseline,
} from "@mui/material";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1976d2",
    },
  },
});

function App() {
  const [count, setCount] = useState(0);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="sm">
        <Box sx={{ my: 4, textAlign: "center" }}>
          <Typography variant="h2" component="h1" gutterBottom>
            Tournament Widget
          </Typography>
          <Typography
            variant="h5"
            component="h2"
            gutterBottom
            color="text.secondary"
          >
            Vite + React + Material UI
          </Typography>

          <Card sx={{ mt: 4 }}>
            <CardContent>
              <Button
                variant="contained"
                size="large"
                onClick={() => setCount((count) => count + 1)}
                sx={{ mb: 2 }}
              >
                Count is {count}
              </Button>
              <Typography variant="body1">
                Edit <code>src/App.tsx</code> and save to test HMR
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
