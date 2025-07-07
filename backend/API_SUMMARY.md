# Tournament Widget API - End-to-End Functionality

## **API Endpoints**

#### Tournament Management

- `POST /api/tournament` - Create tournament with prompts (supports AI generation)
- `GET /api/tournament/{id}/status` - Comprehensive tournament status
- `POST /api/tournament/{id}/start-bracket` - Auto-generate tournament bracket

#### Match Management

- `GET /api/tournament/{id}/matches` - Get all matches (with optional round filter)
- `POST /api/match/{id}/result` - Submit result AND auto-advance tournament

#### Utility

- `GET /api/prompts` - Get all prompts
- `POST /api/test-prompt` - Test prompts with OpenAI

## Complete End-to-End Workflow

### 1. Create Tournament

**Basic Tournament Creation:**

```bash
curl -X POST http://localhost:5001/api/tournament \
  -H "Content-Type: application/json" \
  -d '{
    "input_question": "What is the best movie genre?",
    "custom_prompts": [
      "Which movie genre is the best?",
      "What genre of movies do you prefer?",
      "Tell me the top movie genre",
      "What is your favorite film genre?"
    ],
    "total_prompts": 4
  }'
```

**Tournament with AI Prompt Generation:**

```bash
curl -X POST http://localhost:5001/api/tournament \
  -H "Content-Type: application/json" \
  -d '{
    "input_question": "What is the capital of France?",
    "custom_prompts": [
      "Tell me the capital of France",
      "What city is the capital of France?"
    ],
    "total_prompts": 8
  }'
```

_Note: When fewer than `total_prompts` are provided, the system automatically generates additional prompts using AI._

**Odd Number Tournament (with bye logic):**

```bash
curl -X POST http://localhost:5001/api/tournament \
  -H "Content-Type: application/json" \
  -d '{
    "input_question": "What is the best pet?",
    "custom_prompts": [
      "What pet is the best?",
      "Which pet do you prefer?",
      "Tell me the top pet"
    ],
    "total_prompts": 3
  }'
```

_Note: Odd numbers are supported - some prompts will receive automatic "byes" to the next round._

**Response:**

```json
{
  "tournament_id": 4,
  "input_question": "What is the best movie genre?",
  "prompts": [
    "Which movie genre is the best?",
    "What genre of movies do you prefer?",
    "Tell me the top movie genre",
    "What is your favorite film genre?"
  ]
}
```

### 2. Start Tournament Bracket

```bash
curl -X POST http://localhost:5001/api/tournament/4/start-bracket
```

**Response:**

```json
{
  "message": "Tournament bracket started",
  "tournament_id": 4,
  "round_1_matches": [
    {
      "prompt_1": "Which movie genre is the best?",
      "prompt_2": "What is your favorite film genre?"
    },
    {
      "prompt_1": "What genre of movies do you prefer?",
      "prompt_2": "Tell me the top movie genre"
    }
  ],
  "total_matches": 2
}
```

### 3. Get Tournament Status

```bash
curl -X GET http://localhost:5001/api/tournament/4/status
```

**Response:**

```json
{
  "tournament_id": 4,
  "input_question": "What is the best movie genre?",
  "status": "in_progress",
  "current_round": 1,
  "total_prompts": 4,
  "progress": {
    "total_matches": 2,
    "completed_matches": 0,
    "completion_percentage": 0.0
  },
  "rounds": {
    "1": [
      {
        "match_id": 8,
        "prompt_1": "Which movie genre is the best?",
        "prompt_2": "What is your favorite film genre?",
        "status": "pending",
        "winner": null
      },
      {
        "match_id": 9,
        "prompt_1": "What genre of movies do you prefer?",
        "prompt_2": "Tell me the top movie genre",
        "status": "pending",
        "winner": null
      }
    ]
  },
  "winner": null
}
```

### 4. Submit Match Results (Auto-Advances Tournament)

```bash
curl -X POST http://localhost:5001/api/match/8/result \
  -H "Content-Type: application/json" \
  -d '{"winner_id": 13}'
```

**Response:**

```json
{
  "message": "Match result stored successfully",
  "match_id": 8,
  "winner": "Which movie genre is the best?",
  "round_completed": false
}
```

When the final match of a round is completed, the response includes:

```json
{
  "message": "Match result stored successfully",
  "match_id": 9,
  "winner": "Tell me the top movie genre",
  "round_completed": true,
  "next_round_created": true,
  "next_round": 2,
  "next_round_matches": [
    {
      "prompt_1": "Which movie genre is the best?",
      "prompt_2": "Tell me the top movie genre"
    }
  ]
}
```

**For odd number tournaments, bye winners are also reported:**

```json
{
  "message": "Match result stored successfully",
  "match_id": 1,
  "winner": "What pet is the best?",
  "round_completed": true,
  "next_round_created": true,
  "next_round": 2,
  "bye_winner": "Which pet do you prefer?",
  "next_round_matches": [
    {
      "prompt_1": "What pet is the best?",
      "prompt_2": "Which pet do you prefer?"
    }
  ]
}
```

When tournament is completed:

```json
{
  "message": "Match result stored successfully",
  "match_id": 10,
  "winner": "Which movie genre is the best?",
  "round_completed": true,
  "tournament_completed": true,
  "tournament_winner": "Which movie genre is the best?"
}
```

## Key Features

### ✅ **Automatic Bracket Generation**

- Randomly pairs prompts for first round
- Automatically creates subsequent rounds when previous round completes
- Handles tournament progression without manual intervention
- **Supports odd numbers with bye logic**

### ✅ **AI-Powered Prompt Generation**

- Automatically generates additional prompts when needed
- Uses OpenAI API for intelligent prompt creation
- Fallback generation when AI is unavailable
- Ensures all prompts are unique

### ✅ **Comprehensive Tournament Status**

- Real-time progress tracking
- Round-by-round match details
- Tournament completion detection
- Winner identification
- Bye tracking for odd tournaments

### ✅ **Robust Error Handling**

- Validates match participants
- Prevents duplicate match results
- Handles non-existent tournaments/matches
- Proper HTTP status codes
- Input validation for tournament parameters

### ✅ **Clean API Design**

- No redundant endpoints
- Clear separation of concerns
- Intuitive workflow progression
- Consistent response formats

## Testing

### Safe Test Runner (Recommended)

Use our safe test runner to prevent accidental testing against live servers:

```bash
# Run safe tests (no live server dependencies)
python run_tests.py safe

# Run only unit tests (fastest)
python run_tests.py unit

# Run only integration tests
python run_tests.py integration

# Run all tests (includes potentially risky ones)
python run_tests.py all
```

### Traditional pytest

```bash
# Run all safe tests
python -m pytest tests/test_app.py tests/test_integration_safe.py -v

# Run by test category
python -m pytest -m unit -v      # Unit tests only
python -m pytest -m integration -v  # Integration tests only
```

### Live API Testing

Start the server:

```bash
flask run  # Runs on http://localhost:5001
```

### Full Simulation

Run the complete tournament simulation:

```bash
python tests/simulate_tournament.py
```

### API Examples

**Test prompt endpoint:**

```bash
python tests/example_test_prompt.py
```

**API usage examples:**

```bash
python tests/example_usage.py
```

## Database Schema

The existing database schema supports all new functionality:

- `tournaments` - Tournament metadata
- `matches` - Individual match data with round numbers
- `prompts` - Prompt text and metadata
- `prompt_metadata` - Win/loss statistics per tournament
