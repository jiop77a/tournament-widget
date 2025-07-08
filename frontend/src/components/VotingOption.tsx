import React from "react";
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  Paper,
} from "@mui/material";
import {
  ThumbUp as VoteIcon,
  Psychology as TestIcon,
} from "@mui/icons-material";

interface VotingOptionProps {
  label: string;
  prompt: string;
  promptId: number;
  loading: boolean;
  onVote: (promptId: number) => void;
  onTest: (prompt: string) => void;
}

export const VotingOption: React.FC<VotingOptionProps> = ({
  label,
  prompt,
  promptId,
  loading,
  onVote,
  onTest,
}) => {
  return (
    <Paper
      elevation={3}
      sx={{
        flex: 1,
        p: 3,
        textAlign: "center",
        cursor: loading ? "default" : "pointer",
        border: "2px solid transparent",
        "&:hover": loading
          ? {}
          : {
              borderColor: "primary.main",
              backgroundColor: "action.hover",
            },
        transition: "all 0.2s ease-in-out",
      }}
      onClick={loading ? undefined : () => onVote(promptId)}
    >
      <Typography variant="h6" gutterBottom color="primary.main">
        {label}
      </Typography>
      <Typography variant="body1" sx={{ mb: 3, minHeight: "3em" }}>
        {prompt}
      </Typography>
      <Box sx={{ display: "flex", gap: 1, flexDirection: "column" }}>
        <Button
          variant="contained"
          startIcon={loading ? <CircularProgress size={20} /> : <VoteIcon />}
          disabled={loading}
          fullWidth
          onClick={(e) => {
            e.stopPropagation();
            if (!loading) onVote(promptId);
          }}
        >
          {loading ? "Submitting..." : "Vote for This"}
        </Button>
        <Button
          variant="outlined"
          startIcon={<TestIcon />}
          disabled={loading}
          fullWidth
          onClick={(e) => {
            e.stopPropagation();
            if (!loading) onTest(prompt);
          }}
        >
          Test with AI
        </Button>
      </Box>
    </Paper>
  );
};
