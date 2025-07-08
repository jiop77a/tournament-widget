import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
} from "@mui/material";
import { ArrowBack as BackIcon } from "@mui/icons-material";
import { apiService } from "../services/api";
import type { Match, SubmitMatchResultResponse } from "../types";
import { VotingOption } from "./VotingOption";
import { TestResultDialog } from "./TestResultDialog";

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
  const [testDialogOpen, setTestDialogOpen] = useState(false);
  const [testingPrompt, setTestingPrompt] = useState<string | null>(null);
  const [testLoading, setTestLoading] = useState(false);
  const [testResult, setTestResult] = useState<{
    prompt: string;
    response: string;
    model: string;
    usage: {
      prompt_tokens: number;
      completion_tokens: number;
      total_tokens: number;
    };
  } | null>(null);
  const [testError, setTestError] = useState<string | null>(null);

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

  const handleTestPrompt = async (prompt: string) => {
    setTestError(null);
    setTestLoading(true);
    setTestingPrompt(prompt);
    setTestDialogOpen(true);

    try {
      const response = await apiService.testPrompt({ prompt });
      setTestResult(response);
    } catch (err) {
      setTestError(
        err instanceof Error ? err.message : "Failed to test prompt"
      );
    } finally {
      setTestLoading(false);
    }
  };

  const handleCloseTestDialog = () => {
    setTestDialogOpen(false);
    setTestResult(null);
    setTestError(null);
    setTestingPrompt(null);
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
        <VotingOption
          label="Option A"
          prompt={match.prompt_1}
          promptId={match.prompt_1_id}
          loading={loading}
          onVote={handleVote}
          onTest={handleTestPrompt}
        />

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
        <VotingOption
          label="Option B"
          prompt={match.prompt_2}
          promptId={match.prompt_2_id}
          loading={loading}
          onVote={handleVote}
          onTest={handleTestPrompt}
        />
      </Box>

      {/* Test Result Dialog */}
      <TestResultDialog
        open={testDialogOpen}
        onClose={handleCloseTestDialog}
        testingPrompt={testingPrompt}
        loading={testLoading}
        error={testError}
        result={testResult}
      />
    </Box>
  );
};
