import React, { useState, useEffect } from "react";
import {
  Box,
  Alert,
  Typography,
  Chip,
  Collapse,
  IconButton,
} from "@mui/material";
import {
  Close as CloseIcon,
  EmojiEvents as TrophyIcon,
} from "@mui/icons-material";
import type { SubmitMatchResultResponse } from "../types/api";

interface MatchResultBannersProps {
  matchResult: SubmitMatchResultResponse | null;
}

export const MatchResultBanners: React.FC<MatchResultBannersProps> = ({
  matchResult,
}) => {
  const [show, setShow] = useState(false);

  // Show banners when new match result arrives
  useEffect(() => {
    if (matchResult) {
      setShow(true);

      // Auto-hide banners after 8 seconds
      const timer = setTimeout(() => {
        setShow(false);
      }, 8000);

      return () => clearTimeout(timer);
    }
  }, [matchResult]);

  if (!matchResult || !show) {
    return null;
  }

  return (
    <Box sx={{ mb: 3 }}>
      {/* Vote Success Banner */}
      <Collapse in={show}>
        <Alert
          severity="success"
          sx={{ mb: 2 }}
          action={
            <IconButton
              aria-label="close"
              color="inherit"
              size="small"
              onClick={() => setShow(false)}
            >
              <CloseIcon fontSize="inherit" />
            </IconButton>
          }
        >
          <Typography variant="body1" fontWeight="bold">
            ✅ Vote submitted successfully! Winner: {matchResult.winner}
          </Typography>
        </Alert>
      </Collapse>

      {/* Round Completed Banner */}
      {matchResult.round_completed && (
        <Collapse in={show}>
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body1">
              🎉 Round completed!
              {matchResult.next_round &&
                ` Round ${matchResult.next_round} has been created.`}
            </Typography>
            {matchResult.next_round_matches &&
              matchResult.next_round_matches.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    Next round matches:
                  </Typography>
                  {matchResult.next_round_matches.map((nextMatch, index) => (
                    <Chip
                      key={index}
                      label={`${nextMatch.prompt_1} vs ${nextMatch.prompt_2}`}
                      size="small"
                      sx={{ mr: 1, mt: 0.5 }}
                    />
                  ))}
                </Box>
              )}
            {matchResult.bye_prompts && matchResult.bye_prompts.length > 0 && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Automatic advancement (byes):
                </Typography>
                {matchResult.bye_prompts.map((byePrompt, index) => (
                  <Chip
                    key={index}
                    label={`${byePrompt} (bye)`}
                    size="small"
                    color="secondary"
                    variant="outlined"
                    sx={{ mr: 1, mt: 0.5 }}
                  />
                ))}
              </Box>
            )}
          </Alert>
        </Collapse>
      )}

      {/* Tournament Completed Banner */}
      {matchResult.tournament_completed && (
        <Collapse in={show}>
          <Alert severity="success" sx={{ mb: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <TrophyIcon sx={{ mr: 1, color: "gold" }} />
              <Typography variant="h6" fontWeight="bold">
                🏆 Tournament Complete! Champion:{" "}
                {matchResult.tournament_winner}
              </Typography>
            </Box>
          </Alert>
        </Collapse>
      )}
    </Box>
  );
};
