import React from "react";
import {
  Box,
  Typography,
  Paper,
} from "@mui/material";
import {
  EmojiEvents as TrophyIcon,
  CheckCircle as CompleteIcon,
  Schedule as PendingIcon,
} from "@mui/icons-material";
import type { Match } from "../types";

interface MatchCardProps {
  match: Match;
  onClick?: () => void;
  isLast?: boolean;
}

export const MatchCard: React.FC<MatchCardProps> = ({
  match,
  onClick,
  isLast,
}) => {
  const getStatusIcon = () => {
    switch (match.status) {
      case "completed":
        return <CompleteIcon color="success" fontSize="small" />;
      case "pending":
        return <PendingIcon color="warning" fontSize="small" />;
      default:
        return <PendingIcon color="disabled" fontSize="small" />;
    }
  };

  return (
    <Paper
      elevation={match.status === "pending" ? 4 : 2}
      sx={{
        p: 2,
        cursor: onClick && match.status === "pending" ? "pointer" : "default",
        border: match.status === "pending" ? "2px solid" : "1px solid",
        borderColor: match.status === "pending" ? "primary.main" : "divider",
        backgroundColor:
          match.status === "completed" ? "success.light" : "background.paper",
        minWidth: "240px",
        maxWidth: "240px",
        "&:hover":
          onClick && match.status === "pending"
            ? {
                backgroundColor: "action.hover",
                borderColor: "primary.dark",
                transform: "translateY(-2px)",
                boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
              }
            : {},
        transition: "all 0.3s ease-in-out",
        position: "relative",
      }}
      onClick={onClick && match.status === "pending" ? onClick : undefined}
    >
      {/* Match header */}
      <Box sx={{ display: "flex", alignItems: "center", mb: 1.5 }}>
        {getStatusIcon()}
        <Typography variant="caption" sx={{ ml: 1, fontWeight: "bold" }}>
          Match #{match.match_id}
        </Typography>
        {isLast && (
          <Typography
            variant="caption"
            sx={{ ml: "auto", fontWeight: "bold", color: "primary.main" }}
          >
            FINAL
          </Typography>
        )}
      </Box>

      {/* Contestants */}
      <Box sx={{ mb: 1 }}>
        <Box
          sx={{
            p: 1.5,
            backgroundColor:
              match.winner === match.prompt_1 ? "success.main" : "grey.100",
            borderRadius: 1,
            mb: 1,
            border: match.winner === match.prompt_1 ? "2px solid" : "1px solid",
            borderColor:
              match.winner === match.prompt_1 ? "success.dark" : "grey.300",
            position: "relative",
          }}
        >
          <Typography
            variant="body2"
            sx={{
              fontWeight: match.winner === match.prompt_1 ? "bold" : "normal",
              color:
                match.winner === match.prompt_1
                  ? "success.contrastText"
                  : "text.primary",
              fontSize: "0.875rem",
            }}
          >
            {match.prompt_1}
          </Typography>
          {match.winner === match.prompt_1 && (
            <Box
              sx={{
                position: "absolute",
                right: 8,
                top: "50%",
                transform: "translateY(-50%)",
              }}
            >
              <TrophyIcon sx={{ fontSize: 16, color: "gold" }} />
            </Box>
          )}
        </Box>

        <Typography
          variant="body2"
          sx={{
            textAlign: "center",
            my: 1,
            fontWeight: "bold",
            color: "text.secondary",
          }}
        >
          VS
        </Typography>

        <Box
          sx={{
            p: 1.5,
            backgroundColor:
              match.winner === match.prompt_2 ? "success.main" : "grey.100",
            borderRadius: 1,
            border: match.winner === match.prompt_2 ? "2px solid" : "1px solid",
            borderColor:
              match.winner === match.prompt_2 ? "success.dark" : "grey.300",
            position: "relative",
          }}
        >
          <Typography
            variant="body2"
            sx={{
              fontWeight: match.winner === match.prompt_2 ? "bold" : "normal",
              color:
                match.winner === match.prompt_2
                  ? "success.contrastText"
                  : "text.primary",
              fontSize: "0.875rem",
            }}
          >
            {match.prompt_2}
          </Typography>
          {match.winner === match.prompt_2 && (
            <Box
              sx={{
                position: "absolute",
                right: 8,
                top: "50%",
                transform: "translateY(-50%)",
              }}
            >
              <TrophyIcon sx={{ fontSize: 16, color: "gold" }} />
            </Box>
          )}
        </Box>
      </Box>

      {match.status === "pending" && onClick && (
        <Box sx={{ textAlign: "center", mt: 1 }}>
          <Typography
            variant="caption"
            color="primary.main"
            sx={{ fontWeight: "bold" }}
          >
            Click to vote
          </Typography>
        </Box>
      )}
    </Paper>
  );
};
