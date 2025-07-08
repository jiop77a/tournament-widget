// Test utilities for React components
import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';

// Create a test theme (same as app theme)
const testTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
  },
});

// Custom render function that includes Material UI theme
const AllTheProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <ThemeProvider theme={testTheme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
};

const customRender = (ui: React.ReactElement, options?: Omit<RenderOptions, 'wrapper'>) =>
  render(ui, { wrapper: AllTheProviders, ...options });

// Re-export everything
export * from '@testing-library/react';
export { customRender as render };

// Mock API responses
export const mockApiResponses = {
  createTournament: {
    tournament_id: 1,
    input_question: 'What is the best programming language?',
    prompts: [
      'Which programming language is the best?',
      'What programming language do you prefer?',
      'Tell me the top programming language',
      'What is your favorite programming language?',
    ],
  },
  tournamentStatus: {
    tournament_id: 1,
    input_question: 'What is the best programming language?',
    status: 'in_progress',
    current_round: 1,
    total_prompts: 4,
    progress: {
      total_matches: 2,
      completed_matches: 0,
      completion_percentage: 0.0,
    },
    rounds: {
      '1': [
        {
          match_id: 1,
          prompt_1: 'Which programming language is the best?',
          prompt_2: 'What programming language do you prefer?',
          status: 'pending',
          winner: null,
        },
        {
          match_id: 2,
          prompt_1: 'Tell me the top programming language',
          prompt_2: 'What is your favorite programming language?',
          status: 'pending',
          winner: null,
        },
      ],
    },
    winner: null,
  },
};

// Helper to mock fetch responses
export const mockFetch = (response: any, status = 200) => {
  (global.fetch as any).mockResolvedValueOnce({
    ok: status >= 200 && status < 300,
    status,
    json: async () => response,
  });
};

// Helper to mock fetch errors
export const mockFetchError = (error: string, status = 500) => {
  (global.fetch as any).mockResolvedValueOnce({
    ok: false,
    status,
    json: async () => ({ error }),
  });
};
