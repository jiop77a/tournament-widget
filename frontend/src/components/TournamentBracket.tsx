import React from "react";
import { Box, Card, CardContent } from "@mui/material";
import { TournamentHeader } from "./TournamentHeader";
import { TournamentStartView } from "./TournamentStartView";
import { TournamentTree } from "./TournamentTree";
import type { Tournament, Match } from "../types";

interface TournamentBracketProps {
  tournament: Tournament;
  onMatchClick?: (match: Match) => void;
  onStartBracket?: () => void;
}

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
      <TournamentStartView
        tournament={tournament}
        onStartBracket={onStartBracket}
      />
    );
  }

  return (
    <Box>
      {/* Tournament Header */}
      <TournamentHeader tournament={tournament} />

      {/* Tournament Tree Display */}
      <Card sx={{ mb: 3 }}>
        <CardContent sx={{ p: 0 }}>
          <TournamentTree tournament={tournament} onMatchClick={onMatchClick} />
        </CardContent>
      </Card>
    </Box>
  );
};
