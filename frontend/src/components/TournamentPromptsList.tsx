import React from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Paper,
} from "@mui/material";
import type { Tournament } from "../types";

interface TournamentPromptsListProps {
  tournament: Tournament;
}

export const TournamentPromptsList: React.FC<TournamentPromptsListProps> = ({
  tournament,
}) => {
  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography
          variant="h6"
          gutterBottom
          sx={{ display: "flex", alignItems: "center", gap: 1 }}
        >
          📝 Tournament Prompts
          <Chip
            label={`${tournament.total_prompts} prompts`}
            size="small"
            color="primary"
          />
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          These prompts will compete in the tournament bracket:
        </Typography>

        {/* Tournament Prompts Grid */}
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: 2,
            mb: 3,
          }}
        >
          {tournament.prompts && tournament.prompts.length > 0 ? (
            tournament.prompts.map((prompt, index) => (
              <Paper
                key={index}
                sx={{
                  p: 2,
                  backgroundColor: "background.paper",
                  border: "1px solid",
                  borderColor: "divider",
                  borderRadius: 2,
                  transition: "all 0.2s ease-in-out",
                  "&:hover": {
                    borderColor: "primary.main",
                    boxShadow: 1,
                  },
                }}
              >
                <Box
                  sx={{ display: "flex", alignItems: "flex-start", gap: 1 }}
                >
                  <Chip
                    label={`#${index + 1}`}
                    size="small"
                    color="primary"
                    variant="outlined"
                    sx={{ flexShrink: 0, mt: 0.5 }}
                  />
                  <Typography
                    variant="body2"
                    sx={{ flexGrow: 1, lineHeight: 1.5 }}
                  >
                    {prompt}
                  </Typography>
                </Box>
              </Paper>
            ))
          ) : (
            <Paper
              sx={{ p: 3, backgroundColor: "grey.50", textAlign: "center" }}
            >
              <Typography variant="body2" color="text.secondary">
                Loading tournament prompts...
              </Typography>
            </Paper>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};
