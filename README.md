# Tournament Widget

A web application for creating and managing prompt tournaments with AI-generated content.

## Features

- **Tournament Creation**: Create tournaments with custom prompts
- **AI Prompt Generation**: Automatically generate additional prompts using OpenAI API
- **Bracket Management**: Automatic tournament bracket creation and progression
- **Match Voting**: Vote on matches to advance prompts through rounds
- **Real-time Results**: Track tournament progress and view winners

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+ (for frontend)
- OpenAI API key (for AI prompt generation)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file in project root with:
# OPENAI_API_KEY=your_openai_api_key_here
# FLASK_RUN_PORT=5001
# FLASK_TEST_PORT=5002

# Set up database
flask db upgrade

# Start the backend server
flask run
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5001
- **API Documentation**: See `backend/API_SUMMARY.md`

## Development

### Running Tests

```bash
# Backend tests (recommended - includes safety checks)
cd backend
python run_tests.py all

# Or run specific test types
python run_tests.py unit        # Unit tests only
python run_tests.py integration # Integration tests only
```

### Database Management

```bash
# Check migration status
flask db current

# Create new migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade
```

### API Examples

```bash
# Test the API with example scripts
cd backend
python tests/example_usage.py        # Tournament creation examples
python tests/simulate_tournament.py  # Full tournament simulation
python tests/example_test_prompt.py  # Prompt testing examples
```

## Project Structure

```
tournament-widget/
├── backend/                 # Flask API server
│   ├── services/           # Business logic services
│   ├── tests/              # Test files and examples
│   ├── migrations/         # Database migrations
│   ├── models.py           # Database models
│   ├── tournament_routes.py # API routes
│   └── app.py              # Flask application
├── frontend/               # React frontend
│   ├── src/                # Source code
│   └── public/             # Static assets
└── README.md               # This file
```

## Documentation

- **API Documentation**: `backend/API_SUMMARY.md`
- **Testing Guide**: `backend/TESTING.md`
- **Frontend**: See `frontend/` directory

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python run_tests.py all`
5. Submit a pull request

## License

[Add your license information here]
