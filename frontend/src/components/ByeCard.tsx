import React from "react";
import { Box, Typography, Chip, Paper } from "@mui/material";

interface ByeCardProps {
  prompt: string;
  showConnectionLine?: boolean;
}

export const ByeCard: React.FC<ByeCardProps> = ({
  prompt,
  showConnectionLine = false,
}) => {
  return (
    <Paper
      sx={{
        p: 2,
        mb: 1,
        backgroundColor: "secondary.light",
        border: "2px dashed",
        borderColor: "secondary.main",
        borderRadius: 2,
        textAlign: "center",
        minWidth: "250px",
        position: "relative",
      }}
    >
      <Typography
        variant="body2"
        sx={{
          fontWeight: "bold",
          color: "secondary.dark",
          mb: 0.5,
        }}
      >
        🎯 Automatic Advancement
      </Typography>
      <Typography
        variant="body2"
        sx={{
          color: "text.primary",
          fontStyle: "italic",
        }}
      >
        {prompt}
      </Typography>
      <Chip
        label="BYE"
        size="small"
        color="secondary"
        sx={{ mt: 1 }}
      />

      {/* Connection line to next round for byes */}
      {showConnectionLine && (
        <Box
          sx={{
            position: "absolute",
            right: "-32px",
            top: "50%",
            transform: "translateY(-50%)",
            width: "32px",
            height: "2px",
            backgroundColor: "secondary.main",
            zIndex: 1,
            "&::after": {
              content: '""',
              position: "absolute",
              right: "-6px",
              top: "-3px",
              width: 0,
              height: 0,
              borderLeft: "6px solid",
              borderLeftColor: "secondary.main",
              borderTop: "4px solid transparent",
              borderBottom: "4px solid transparent",
            },
          }}
        />
      )}
    </Paper>
  );
};
