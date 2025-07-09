import React, { useState, useEffect } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  IconButton,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  Divider,
} from "@mui/material";
import { Add as AddIcon, Delete as DeleteIcon } from "@mui/icons-material";
import { apiService } from "../services/api";
import type { CreateTournamentResponse } from "../types";

interface TournamentCreationFormProps {
  onTournamentCreated?: (tournament: CreateTournamentResponse) => void;
}

export const TournamentCreationForm: React.FC<TournamentCreationFormProps> = ({
  onTournamentCreated,
}) => {
  const [inputQuestion, setInputQuestion] = useState("");
  const [customPrompts, setCustomPrompts] = useState<string[]>([""]);
  const [totalPrompts, setTotalPrompts] = useState<number | "">(8);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<CreateTournamentResponse | null>(null);
  const [openAIAvailable, setOpenAIAvailable] = useState<boolean | null>(null);

  // Check OpenAI availability on component mount
  useEffect(() => {
    const checkOpenAIStatus = async () => {
      try {
        const status = await apiService.getOpenAIStatus();
        setOpenAIAvailable(status.available);
      } catch (err) {
        console.error("Failed to check OpenAI status:", err);
        setOpenAIAvailable(false);
      }
    };

    checkOpenAIStatus();
  }, []);

  const handleAddPrompt = () => {
    setCustomPrompts([...customPrompts, ""]);
  };

  const handleRemovePrompt = (index: number) => {
    if (customPrompts.length > 1) {
      setCustomPrompts(customPrompts.filter((_, i) => i !== index));
    }
  };

  const handlePromptChange = (index: number, value: string) => {
    const newPrompts = [...customPrompts];
    newPrompts[index] = value;
    setCustomPrompts(newPrompts);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      // Filter out empty prompts
      const validPrompts = customPrompts.filter(
        (prompt) => prompt.trim() !== ""
      );

      if (!inputQuestion.trim()) {
        throw new Error("Input question is required");
      }

      if (typeof totalPrompts !== "number" || totalPrompts < 2) {
        throw new Error("Total prompts must be at least 2 for a tournament");
      }

      // Check if we have enough prompts when OpenAI is not available
      if (openAIAvailable === false && validPrompts.length < totalPrompts) {
        throw new Error(
          `Not enough prompts provided. You provided ${validPrompts.length} prompts but need ${totalPrompts}. Either provide more prompts or set up an OpenAI API key for automatic prompt generation.`
        );
      }

      const response = await apiService.createTournament({
        input_question: inputQuestion.trim(),
        custom_prompts: validPrompts,
        total_prompts: totalPrompts as number,
      });

      setSuccess(response);
      onTournamentCreated?.(response);

      // Reset form
      setInputQuestion("");
      setCustomPrompts([""]);
      setTotalPrompts(8);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to create tournament"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setInputQuestion("");
    setCustomPrompts([""]);
    setTotalPrompts(8);
    setError(null);
    setSuccess(null);
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" component="h2" gutterBottom>
          Create New Tournament
        </Typography>

        {openAIAvailable === false && (
          <Alert severity="info" sx={{ mb: 2 }}>
            <strong>AI Prompt Generation Unavailable:</strong> OpenAI API key
            not configured. You'll need to provide all prompts manually or set
            up an OpenAI API key to enable automatic prompt generation.
          </Alert>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Tournament created successfully! ID: {success.tournament_id}
            <br />
            Generated {success.prompts.length} prompts total.
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <TextField
            fullWidth
            label="Tournament Question"
            placeholder="e.g., What is the best programming language?"
            value={inputQuestion}
            onChange={(e) => setInputQuestion(e.target.value)}
            margin="normal"
            required
            helperText="The main question that prompts will be variations of"
          />

          <TextField
            fullWidth
            type="number"
            label="Total Prompts"
            value={totalPrompts}
            onChange={(e) => {
              const value = e.target.value;
              if (value === "") {
                setTotalPrompts("");
              } else {
                const parsed = parseInt(value);
                if (!isNaN(parsed)) {
                  setTotalPrompts(parsed);
                }
              }
            }}
            margin="normal"
            error={typeof totalPrompts !== "number" || totalPrompts < 2}
            slotProps={{
              htmlInput: { min: 2, max: 32 },
            }}
            helperText={
              typeof totalPrompts !== "number"
                ? "Please enter a number (minimum 2)"
                : totalPrompts < 2
                ? "Must be at least 2 prompts for a tournament"
                : "Total number of prompts in the tournament (AI will generate additional prompts if needed)"
            }
          />

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            Custom Prompts
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Add your own prompt variations. If you provide fewer than the total
            prompts needed, AI will generate additional ones automatically.
          </Typography>

          {customPrompts.map((prompt, index) => (
            <Box key={index} sx={{ display: "flex", gap: 1, mb: 2 }}>
              <TextField
                fullWidth
                label={`Prompt ${index + 1}`}
                placeholder="e.g., Which programming language is the best?"
                value={prompt}
                onChange={(e) => handlePromptChange(index, e.target.value)}
                size="small"
              />
              <IconButton
                onClick={() => handleRemovePrompt(index)}
                disabled={customPrompts.length === 1}
                color="error"
                aria-label={`Delete prompt ${index + 1}`}
              >
                <DeleteIcon />
              </IconButton>
            </Box>
          ))}

          <Button
            startIcon={<AddIcon />}
            onClick={handleAddPrompt}
            variant="outlined"
            size="small"
            sx={{ mb: 3 }}
          >
            Add Another Prompt
          </Button>

          <Box sx={{ display: "flex", gap: 2, justifyContent: "flex-end" }}>
            <Button
              type="button"
              variant="outlined"
              onClick={handleReset}
              disabled={loading}
            >
              Reset
            </Button>
            <Button
              type="submit"
              variant="contained"
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} /> : null}
            >
              {loading ? "Creating..." : "Create Tournament"}
            </Button>
          </Box>
        </Box>

        {success && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Generated Prompts:
            </Typography>
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
              {success.prompts.map((prompt, index) => (
                <Chip
                  key={index}
                  label={prompt}
                  variant="outlined"
                  size="small"
                />
              ))}
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
