import React from "react";
import { Box, Typography, Chip } from "@mui/material";
import { MatchCard } from "./MatchCard";
import { TournamentWinner } from "./TournamentWinner";
import type { Tournament, Match } from "../types";

interface TournamentTreeProps {
  tournament: Tournament;
  onMatchClick?: (match: Match) => void;
}

export const TournamentTree: React.FC<TournamentTreeProps> = ({
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
                  <MatchCard
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
        {tournament.winner && <TournamentWinner winner={tournament.winner} />}
      </Box>
    </Box>
  );
};
