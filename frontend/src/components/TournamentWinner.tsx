import React from "react";
import {
  Box,
  Typography,
  Paper,
} from "@mui/material";
import {
  EmojiEvents as TrophyIcon,
} from "@mui/icons-material";

interface TournamentWinnerProps {
  winner: string;
}

export const TournamentWinner: React.FC<TournamentWinnerProps> = ({
  winner,
}) => {
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        minWidth: "200px",
      }}
    >
      <TrophyIcon sx={{ fontSize: 48, color: "gold", mb: 2 }} />
      <Typography
        variant="h5"
        sx={{
          fontWeight: "bold",
          color: "success.main",
          textAlign: "center",
          textShadow: "1px 1px 2px rgba(0,0,0,0.1)",
        }}
      >
        Champion!
      </Typography>
      <Paper
        sx={{
          p: 2,
          mt: 2,
          backgroundColor: "success.light",
          border: "2px solid",
          borderColor: "success.main",
          borderRadius: 2,
        }}
      >
        <Typography
          variant="body1"
          sx={{
            fontWeight: "bold",
            color: "success.contrastText",
            textAlign: "center",
          }}
        >
          {winner}
        </Typography>
      </Paper>
    </Box>
  );
};
