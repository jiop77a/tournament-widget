import React from "react";
import { Box, Card, CardContent, Typography, Button } from "@mui/material";
import { PlayArrow as PlayIcon } from "@mui/icons-material";
import { TournamentPromptsList } from "./TournamentPromptsList";
import type { Tournament } from "../types";

interface TournamentStartViewProps {
  tournament: Tournament;
  onStartBracket?: () => void;
}

export const TournamentStartView: React.FC<TournamentStartViewProps> = ({
  tournament,
  onStartBracket,
}) => {
  return (
    <Box>
      {/* Tournament Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
            <Typography variant="h4" component="h1" sx={{ flexGrow: 1 }}>
              {tournament.input_question}
            </Typography>
          </Box>

          <Box sx={{ display: "flex", gap: 3, mb: 2, flexWrap: "wrap" }}>
            <Typography variant="body2" color="text.secondary">
              Status: <strong>Ready to Start</strong>
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Prompts: <strong>{tournament.total_prompts}</strong>
            </Typography>
          </Box>

          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Tournament created successfully! Review the prompts below and
              start the bracket when ready.
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Tournament Prompts Display */}
      <TournamentPromptsList tournament={tournament} />

      {/* Start Tournament Button */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ textAlign: "center", pt: 2 }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<PlayIcon />}
              onClick={onStartBracket}
              sx={{ minWidth: 200 }}
            >
              Start Tournament Bracket
            </Button>
            <Typography
              variant="caption"
              display="block"
              sx={{ mt: 1, color: "text.secondary" }}
            >
              This will create the first round matches and begin the tournament
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};
