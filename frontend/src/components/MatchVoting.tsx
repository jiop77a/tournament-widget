import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Paper,
} from "@mui/material";
import {
  ThumbUp as VoteIcon,
  ArrowBack as BackIcon,
} from "@mui/icons-material";
import { apiService } from "../services/api";
import type { Match, SubmitMatchResultResponse } from "../types";

interface MatchVotingProps {
  match: Match;
  onVoteSubmitted?: (result: SubmitMatchResultResponse) => void;
  onBack?: () => void;
}

export const MatchVoting: React.FC<MatchVotingProps> = ({
  match,
  onVoteSubmitted,
  onBack,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleVote = async (winnerId: number) => {
    setError(null);
    setLoading(true);

    try {
      const response = await apiService.submitMatchResult(
        match.match_id,
        winnerId
      );
      onVoteSubmitted?.(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit vote");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      {/* Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
            <Typography variant="h5" sx={{ flexGrow: 1 }}>
              Vote on Match #{match.match_id}
            </Typography>
            {onBack && (
              <Button
                variant="outlined"
                startIcon={<BackIcon />}
                onClick={onBack}
                disabled={loading}
              >
                Back
              </Button>
            )}
          </Box>
          <Typography variant="body1" color="text.secondary">
            Choose the prompt you think is better:
          </Typography>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Voting Options */}
      <Box
        sx={{
          display: "flex",
          gap: 3,
          flexDirection: { xs: "column", md: "row" },
        }}
      >
        {/* Option 1 */}
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
          onClick={loading ? undefined : () => handleVote(match.prompt_1_id)}
        >
          <Typography variant="h6" gutterBottom color="primary.main">
            Option A
          </Typography>
          <Typography variant="body1" sx={{ mb: 3, minHeight: "3em" }}>
            {match.prompt_1}
          </Typography>
          <Button
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} /> : <VoteIcon />}
            disabled={loading}
            fullWidth
            onClick={(e) => {
              e.stopPropagation();
              if (!loading) handleVote(match.prompt_1_id);
            }}
          >
            {loading ? "Submitting..." : "Vote for This"}
          </Button>
        </Paper>

        {/* VS Divider */}
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            minWidth: { xs: "auto", md: "60px" },
            minHeight: { xs: "40px", md: "auto" },
          }}
        >
          <Typography variant="h4" color="text.secondary" fontWeight="bold">
            VS
          </Typography>
        </Box>

        {/* Option 2 */}
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
          onClick={loading ? undefined : () => handleVote(match.prompt_2_id)}
        >
          <Typography variant="h6" gutterBottom color="primary.main">
            Option B
          </Typography>
          <Typography variant="body1" sx={{ mb: 3, minHeight: "3em" }}>
            {match.prompt_2}
          </Typography>
          <Button
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} /> : <VoteIcon />}
            disabled={loading}
            fullWidth
            onClick={(e) => {
              e.stopPropagation();
              if (!loading) handleVote(match.prompt_2_id);
            }}
          >
            {loading ? "Submitting..." : "Vote for This"}
          </Button>
        </Paper>
      </Box>
    </Box>
  );
};
