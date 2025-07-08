import React from "react";
import {
  Box,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Divider,
  Button,
} from "@mui/material";

interface TestResultDialogProps {
  open: boolean;
  onClose: () => void;
  testingPrompt: string | null;
  loading: boolean;
  error: string | null;
  result: {
    prompt: string;
    response: string;
    model: string;
    usage: {
      prompt_tokens: number;
      completion_tokens: number;
      total_tokens: number;
    };
  } | null;
}

export const TestResultDialog: React.FC<TestResultDialogProps> = ({
  open,
  onClose,
  testingPrompt,
  loading,
  error,
  result,
}) => {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        AI Test Result
        {testingPrompt && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Testing: "{testingPrompt.substring(0, 100)}
            {testingPrompt.length > 100 ? "..." : ""}"
          </Typography>
        )}
      </DialogTitle>
      <DialogContent>
        {loading && (
          <Box sx={{ display: "flex", justifyContent: "center", py: 3 }}>
            <CircularProgress />
            <Typography sx={{ ml: 2 }}>Testing prompt with AI...</Typography>
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {result && (
          <Box>
            <Typography variant="h6" gutterBottom>
              AI Response:
            </Typography>
            <Paper sx={{ p: 2, mb: 3, backgroundColor: "grey.50" }}>
              <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                {result.response}
              </Typography>
            </Paper>

            <Divider sx={{ my: 2 }} />

            <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap", mb: 2 }}>
              <Chip label={`Model: ${result.model}`} size="small" />
              <Chip
                label={`Tokens: ${result.usage.total_tokens}`}
                size="small"
              />
              <Chip
                label={`Prompt: ${result.usage.prompt_tokens}`}
                size="small"
              />
              <Chip
                label={`Response: ${result.usage.completion_tokens}`}
                size="small"
              />
            </Box>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};
