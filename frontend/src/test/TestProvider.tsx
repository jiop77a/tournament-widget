// Test provider component for wrapping components in tests
import React from "react";
import { ThemeProvider, createTheme, CssBaseline } from "@mui/material";

// Create a test theme (same as app theme)
const testTheme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1976d2",
    },
    secondary: {
      main: "#dc004e",
    },
  },
});

export const TestProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  return (
    <ThemeProvider theme={testTheme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
};
