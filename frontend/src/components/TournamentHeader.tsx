import React from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
} from "@mui/material";
import {
  EmojiEvents as TrophyIcon,
} from "@mui/icons-material";
import type { Tournament } from "../types";

interface TournamentHeaderProps {
  tournament: Tournament;
}

export const TournamentHeader: React.FC<TournamentHeaderProps> = ({
  tournament,
}) => {
  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
          <Typography variant="h4" component="h1" sx={{ flexGrow: 1 }}>
            {tournament.input_question}
          </Typography>
          {tournament.winner && (
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <TrophyIcon sx={{ color: "gold", mr: 1 }} />
              <Typography variant="h6" color="success.main">
                Winner!
              </Typography>
            </Box>
          )}
        </Box>

        <Box sx={{ display: "flex", gap: 3, mb: 2, flexWrap: "wrap" }}>
          <Typography variant="body2" color="text.secondary">
            Status: <strong>{tournament.status}</strong>
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Round: <strong>{tournament.current_round}</strong>
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Prompts: <strong>{tournament.total_prompts}</strong>
          </Typography>
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Progress: {tournament.progress.completed_matches} /{" "}
            {tournament.progress.total_matches} matches completed (
            {tournament.progress.completion_percentage}%)
          </Typography>
          <LinearProgress
            variant="determinate"
            value={tournament.progress.completion_percentage}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>

        {tournament.winner && (
          <Box
            sx={{
              p: 2,
              backgroundColor: "success.light",
              borderRadius: 2,
              textAlign: "center",
            }}
          >
            <Typography variant="h6" color="success.contrastText">
              🏆 Tournament Winner: {tournament.winner}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
