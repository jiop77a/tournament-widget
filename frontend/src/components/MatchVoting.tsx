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
  Chip,
} from "@mui/material";
import {
  ThumbUp as VoteIcon,
  CheckCircle as CompleteIcon,
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
  const [result, setResult] = useState<SubmitMatchResultResponse | null>(null);

  const handleVote = async (winnerId: number) => {
    setError(null);
    setLoading(true);

    try {
      const response = await apiService.submitMatchResult(
        match.match_id,
        winnerId
      );
      setResult(response);
      onVoteSubmitted?.(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit vote");
    } finally {
      setLoading(false);
    }
  };

  // If voting is complete, show results
  if (result) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ textAlign: "center", py: 3 }}>
            <CompleteIcon sx={{ fontSize: 48, color: "success.main", mb: 2 }} />
            <Typography variant="h5" gutterBottom color="success.main">
              Vote Submitted Successfully!
            </Typography>

            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Winner: {result.winner}
              </Typography>
              <Chip
                label={`Match #${result.match_id}`}
                color="primary"
                sx={{ mb: 2 }}
              />
            </Box>

            {result.round_completed && (
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  🎉 Round completed!
                  {result.next_round &&
                    ` Round ${result.next_round} has been created.`}
                </Typography>
              </Alert>
            )}

            {result.tournament_completed && (
              <Alert severity="success" sx={{ mb: 2 }}>
                <Typography variant="body1" fontWeight="bold">
                  🏆 Tournament Complete!
                  <br />
                  Champion: {result.tournament_winner}
                </Typography>
              </Alert>
            )}

            {result.next_round_matches &&
              result.next_round_matches.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Next round matches created:
                  </Typography>
                  {result.next_round_matches.map((nextMatch, index) => (
                    <Typography key={index} variant="caption" display="block">
                      {nextMatch.prompt_1} vs {nextMatch.prompt_2}
                    </Typography>
                  ))}
                </Box>
              )}

            <Button
              variant="outlined"
              startIcon={<BackIcon />}
              onClick={onBack}
              sx={{ mt: 2 }}
            >
              Back to Tournament
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
  }

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

      {/* Instructions */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="body2" color="text.secondary" textAlign="center">
            💡 Tip: Consider which prompt would generate better or more
            interesting responses
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};
