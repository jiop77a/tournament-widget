import React from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Grid,
  Divider,
  Paper,
  Button,
} from "@mui/material";
import {
  EmojiEvents as TrophyIcon,
  PlayArrow as PlayIcon,
  CheckCircle as CompleteIcon,
  Schedule as PendingIcon,
} from "@mui/icons-material";
import type { Tournament, Match } from "../types";

interface TournamentBracketProps {
  tournament: Tournament;
  onMatchClick?: (match: Match) => void;
  onStartBracket?: () => void;
}

interface MatchCardProps {
  match: Match;
  onClick?: () => void;
}

const MatchCard: React.FC<MatchCardProps> = ({ match, onClick }) => {
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

  const getStatusColor = () => {
    switch (match.status) {
      case "completed":
        return "success";
      case "pending":
        return "warning";
      default:
        return "default";
    }
  };

  return (
    <Paper
      elevation={2}
      sx={{
        p: 2,
        cursor: onClick && match.status === "pending" ? "pointer" : "default",
        border: match.status === "pending" ? "2px solid" : "1px solid",
        borderColor:
          match.status === "pending" ? "primary.main" : "divider",
        "&:hover":
          onClick && match.status === "pending"
            ? {
                backgroundColor: "action.hover",
                borderColor: "primary.dark",
              }
            : {},
        transition: "all 0.2s ease-in-out",
      }}
      onClick={onClick && match.status === "pending" ? onClick : undefined}
    >
      <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
        {getStatusIcon()}
        <Typography variant="caption" sx={{ ml: 1, fontWeight: "bold" }}>
          Match #{match.match_id}
        </Typography>
        <Chip
          label={match.status}
          size="small"
          color={getStatusColor()}
          sx={{ ml: "auto" }}
        />
      </Box>

      <Box sx={{ mb: 2 }}>
        <Typography
          variant="body2"
          sx={{
            p: 1,
            backgroundColor:
              match.winner === match.prompt_1 ? "success.light" : "grey.100",
            borderRadius: 1,
            mb: 1,
            fontWeight: match.winner === match.prompt_1 ? "bold" : "normal",
            color: match.winner === match.prompt_1 ? "success.contrastText" : "text.primary",
          }}
        >
          {match.prompt_1}
        </Typography>
        <Typography variant="body2" sx={{ textAlign: "center", my: 1 }}>
          VS
        </Typography>
        <Typography
          variant="body2"
          sx={{
            p: 1,
            backgroundColor:
              match.winner === match.prompt_2 ? "success.light" : "grey.100",
            borderRadius: 1,
            fontWeight: match.winner === match.prompt_2 ? "bold" : "normal",
            color: match.winner === match.prompt_2 ? "success.contrastText" : "text.primary",
          }}
        >
          {match.prompt_2}
        </Typography>
      </Box>

      {match.winner && (
        <Box sx={{ textAlign: "center" }}>
          <Typography variant="caption" color="success.main" fontWeight="bold">
            Winner: {match.winner}
          </Typography>
        </Box>
      )}

      {match.status === "pending" && onClick && (
        <Box sx={{ textAlign: "center", mt: 1 }}>
          <Typography variant="caption" color="primary.main">
            Click to vote
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export const TournamentBracket: React.FC<TournamentBracketProps> = ({
  tournament,
  onMatchClick,
  onStartBracket,
}) => {
  // Check if tournament needs to be started
  if (tournament.status === "active" && Object.keys(tournament.rounds).length === 0) {
    return (
      <Card>
        <CardContent sx={{ textAlign: "center", py: 4 }}>
          <PlayIcon sx={{ fontSize: 48, color: "primary.main", mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Ready to Start Tournament
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Tournament "{tournament.input_question}" is ready with{" "}
            {tournament.total_prompts} prompts.
          </Typography>
          <Button
            variant="contained"
            size="large"
            startIcon={<PlayIcon />}
            onClick={onStartBracket}
          >
            Start Tournament Bracket
          </Button>
        </CardContent>
      </Card>
    );
  }

  const rounds = Object.keys(tournament.rounds)
    .map(Number)
    .sort((a, b) => a - b);

  return (
    <Box>
      {/* Tournament Header */}
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

          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={4}>
              <Typography variant="body2" color="text.secondary">
                Status: <strong>{tournament.status}</strong>
              </Typography>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Typography variant="body2" color="text.secondary">
                Round: <strong>{tournament.current_round}</strong>
              </Typography>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Typography variant="body2" color="text.secondary">
                Prompts: <strong>{tournament.total_prompts}</strong>
              </Typography>
            </Grid>
          </Grid>

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

      {/* Rounds Display */}
      {rounds.map((roundNumber) => (
        <Card key={roundNumber} sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Round {roundNumber}
              {roundNumber === tournament.current_round && (
                <Chip
                  label="Current"
                  color="primary"
                  size="small"
                  sx={{ ml: 2 }}
                />
              )}
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <Grid container spacing={2}>
              {tournament.rounds[roundNumber].map((match) => (
                <Grid item xs={12} md={6} lg={4} key={match.match_id}>
                  <MatchCard
                    match={match}
                    onClick={
                      onMatchClick ? () => onMatchClick(match) : undefined
                    }
                  />
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
};
