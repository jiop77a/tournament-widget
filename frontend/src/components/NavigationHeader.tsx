import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Box, Button, Breadcrumbs, Typography, Link } from "@mui/material";
import {
  Home as HomeIcon,
  EmojiEvents as TournamentIcon,
} from "@mui/icons-material";

interface NavigationHeaderProps {
  tournamentId?: number;
  matchId?: number;
}

export const NavigationHeader: React.FC<NavigationHeaderProps> = ({
  tournamentId,
  matchId,
}) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleHomeClick = () => {
    navigate("/");
  };

  const handleTournamentClick = () => {
    if (tournamentId) {
      navigate(`/tournament/${tournamentId}`);
    }
  };

  return (
    <Box
      sx={{ mb: 3, pb: 2, borderBottom: "1px solid", borderColor: "divider" }}
    >
      <Breadcrumbs aria-label="breadcrumb" sx={{ mb: 2 }}>
        <Link
          component="button"
          variant="body1"
          onClick={handleHomeClick}
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 0.5,
            textDecoration: "none",
            color: location.pathname === "/" ? "primary.main" : "text.primary",
            "&:hover": { textDecoration: "underline" },
          }}
        >
          <HomeIcon fontSize="small" />
          Home
        </Link>

        {tournamentId && (
          <Link
            component="button"
            variant="body1"
            onClick={handleTournamentClick}
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 0.5,
              textDecoration: "none",
              color: !matchId ? "primary.main" : "text.primary",
              "&:hover": { textDecoration: "underline" },
            }}
          >
            <TournamentIcon fontSize="small" />
            Tournament #{tournamentId}
          </Link>
        )}

        {matchId && (
          <Typography
            color="text.primary"
            sx={{ display: "flex", alignItems: "center", gap: 0.5 }}
          >
            Match #{matchId}
          </Typography>
        )}
      </Breadcrumbs>

      {location.pathname !== "/" && (
        <Button
          variant="outlined"
          size="small"
          onClick={handleHomeClick}
          startIcon={<HomeIcon />}
        >
          Back to Home
        </Button>
      )}
    </Box>
  );
};
