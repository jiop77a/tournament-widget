import React from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Paper,
  Button,
} from "@mui/material";
import { ShareTournament } from "./ShareTournament";
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

// Tree-style bracket component
interface TournamentTreeProps {
  tournament: Tournament;
  onMatchClick?: (match: Match) => void;
}

const TournamentTree: React.FC<TournamentTreeProps> = ({
  tournament,
  onMatchClick,
}) => {
  const rounds = Object.keys(tournament.rounds)
    .map(Number)
    .sort((a, b) => a - b);

  const maxRounds = rounds.length;

  return (
    <Box
      sx={{
        overflowX: "auto",
        minHeight: "400px",
        p: 2,
        background: "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
        borderRadius: 2,
      }}
    >
      <Box
        sx={{
          display: "flex",
          gap: 4,
          minWidth: `${maxRounds * 300}px`,
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {rounds.map((roundNumber, roundIndex) => (
          <Box
            key={roundNumber}
            sx={{
              display: "flex",
              flexDirection: "column",
              gap: 3,
              minWidth: "280px",
            }}
          >
            {/* Round Header */}
            <Box sx={{ textAlign: "center", mb: 2 }}>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: "bold",
                  color: "primary.main",
                  textShadow: "1px 1px 2px rgba(0,0,0,0.1)",
                }}
              >
                {roundNumber === maxRounds && tournament.winner
                  ? "Final"
                  : `Round ${roundNumber}`}
                {roundNumber === tournament.current_round && (
                  <Chip
                    label="Current"
                    color="primary"
                    size="small"
                    sx={{ ml: 1 }}
                  />
                )}
              </Typography>
            </Box>

            {/* Matches in this round */}
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                gap: 4,
                alignItems: "center",
              }}
            >
              {tournament.rounds[roundNumber].map((match) => (
                <Box key={match.match_id} sx={{ position: "relative" }}>
                  <TreeMatchCard
                    match={match}
                    onClick={
                      onMatchClick ? () => onMatchClick(match) : undefined
                    }
                    isLast={roundIndex === rounds.length - 1}
                  />

                  {/* Connection line to next round */}
                  {roundIndex < rounds.length - 1 && (
                    <Box
                      sx={{
                        position: "absolute",
                        right: "-32px",
                        top: "50%",
                        transform: "translateY(-50%)",
                        width: "32px",
                        height: "2px",
                        backgroundColor: match.winner
                          ? "success.main"
                          : "grey.300",
                        zIndex: 1,
                        "&::after": {
                          content: '""',
                          position: "absolute",
                          right: "-6px",
                          top: "-3px",
                          width: 0,
                          height: 0,
                          borderLeft: "6px solid",
                          borderLeftColor: match.winner
                            ? "success.main"
                            : "grey.300",
                          borderTop: "4px solid transparent",
                          borderBottom: "4px solid transparent",
                        },
                      }}
                    />
                  )}
                </Box>
              ))}
            </Box>
          </Box>
        ))}

        {/* Winner Display */}
        {tournament.winner && (
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
                {tournament.winner}
              </Typography>
            </Paper>
          </Box>
        )}
      </Box>
    </Box>
  );
};

// Tree-style match card component
interface TreeMatchCardProps {
  match: Match;
  onClick?: () => void;
  isLast?: boolean;
}

const TreeMatchCard: React.FC<TreeMatchCardProps> = ({
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

export const TournamentBracket: React.FC<TournamentBracketProps> = ({
  tournament,
  onMatchClick,
  onStartBracket,
}) => {
  // Check if tournament needs to be started
  if (
    tournament.status === "active" &&
    Object.keys(tournament.rounds).length === 0
  ) {
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

            {/* Start Tournament Button */}
            <Box
              sx={{
                textAlign: "center",
                pt: 2,
                borderTop: "1px solid",
                borderColor: "divider",
              }}
            >
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
                This will create the first round matches and begin the
                tournament
              </Typography>
            </Box>
          </CardContent>
        </Card>

        {/* Share Tournament */}
        <ShareTournament tournamentId={tournament.tournament_id} />
      </Box>
    );
  }

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

      {/* Share Tournament */}
      <ShareTournament tournamentId={tournament.tournament_id} />

      {/* Tournament Tree Display */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 0 }}>
          <TournamentTree tournament={tournament} onMatchClick={onMatchClick} />
        </CardContent>
      </Card>
    </Box>
  );
};
