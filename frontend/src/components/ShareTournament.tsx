import React, { useState } from "react";
import {
  Box,
  Button,
  TextField,
  Typography,
  Snackbar,
  Alert,
  Paper,
  IconButton,
  Tooltip,
} from "@mui/material";
import {
  Share as ShareIcon,
  ContentCopy as CopyIcon,
  Link as LinkIcon,
} from "@mui/icons-material";

interface ShareTournamentProps {
  tournamentId: number;
  compact?: boolean;
}

export const ShareTournament: React.FC<ShareTournamentProps> = ({
  tournamentId,
  compact = false,
}) => {
  const [showSnackbar, setShowSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");

  const tournamentUrl = `${window.location.origin}/tournament/${tournamentId}`;

  const handleCopyUrl = async () => {
    try {
      await navigator.clipboard.writeText(tournamentUrl);
      setSnackbarMessage("Tournament URL copied to clipboard!");
      setShowSnackbar(true);
    } catch {
      setSnackbarMessage("Failed to copy URL");
      setShowSnackbar(true);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Tournament #${tournamentId}`,
          text: "Check out this tournament!",
          url: tournamentUrl,
        });
      } catch {
        // User cancelled sharing or sharing failed
        handleCopyUrl(); // Fallback to copying
      }
    } else {
      handleCopyUrl(); // Fallback for browsers without Web Share API
    }
  };

  if (compact) {
    return (
      <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
        <Tooltip title="Copy tournament link">
          <IconButton size="small" onClick={handleCopyUrl}>
            <LinkIcon fontSize="small" />
          </IconButton>
        </Tooltip>

        <Tooltip title="Share tournament">
          <IconButton size="small" onClick={handleShare}>
            <ShareIcon fontSize="small" />
          </IconButton>
        </Tooltip>

        <Snackbar
          open={showSnackbar}
          autoHideDuration={3000}
          onClose={() => setShowSnackbar(false)}
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        >
          <Alert severity="success" onClose={() => setShowSnackbar(false)}>
            {snackbarMessage}
          </Alert>
        </Snackbar>
      </Box>
    );
  }

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography
        variant="h6"
        gutterBottom
        sx={{ display: "flex", alignItems: "center", gap: 1 }}
      >
        <ShareIcon />
        Share Tournament
      </Typography>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Share this tournament with others using the link below:
      </Typography>

      <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
        <TextField
          fullWidth
          value={tournamentUrl}
          variant="outlined"
          size="small"
          InputProps={{
            readOnly: true,
          }}
          sx={{
            "& .MuiInputBase-input": {
              fontSize: "0.875rem",
            },
          }}
        />

        <Button
          variant="outlined"
          onClick={handleCopyUrl}
          startIcon={<CopyIcon />}
          sx={{ minWidth: "auto", px: 2 }}
        >
          Copy
        </Button>
      </Box>

      <Button
        variant="contained"
        onClick={handleShare}
        startIcon={<ShareIcon />}
        fullWidth
      >
        Share Tournament
      </Button>

      <Snackbar
        open={showSnackbar}
        autoHideDuration={3000}
        onClose={() => setShowSnackbar(false)}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert severity="success" onClose={() => setShowSnackbar(false)}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Paper>
  );
};
