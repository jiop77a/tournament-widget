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
- OpenAI API key (optional - for AI prompt generation and testing)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
# Create .env file in project root with:
# OPENAI_API_KEY=your_openai_api_key_here  # Optional - enables AI features
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

> **📖 For detailed frontend development guide, see [`frontend/README.md`](frontend/README.md)**

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5001
- **API Documentation**: See `backend/API_SUMMARY.md`

## Usage Modes

The tournament widget supports two usage modes:

### With OpenAI API Key (Full Features)

- **AI Prompt Generation**: Automatically generates additional prompts when you provide fewer than needed
- **Prompt Testing**: Test prompts with AI to see sample responses
- **Flexible Tournament Creation**: Create tournaments with any number of prompts (minimum 2)

### Without OpenAI API Key (Manual Mode)

- **Manual Prompt Entry**: Provide all prompts manually for your tournament
- **Tournament Creation**: Must provide the exact number of prompts needed for the tournament
- **Core Tournament Features**: Full bracket management, voting, and progression tracking
- **No AI Dependencies**: Works completely offline for prompt management

The application automatically detects whether an OpenAI API key is configured and adjusts the interface accordingly.

## Development

### Running Tests

**Backend Tests:**

```bash
# Backend tests (recommended - includes safety checks)
cd backend
python run_tests.py all

# Or run specific test types
python run_tests.py unit        # Unit tests only
python run_tests.py integration # Integration tests only
```

**Frontend Tests:**

```bash
# Frontend tests
cd frontend
npm run test:run        # Run all tests
npm run test:coverage   # Run with coverage report
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

## Future Improvements

### Core Features

- **User Authentication**: Add user accounts and tournament ownership
- **Tournament Templates**: Pre-built tournament types and configurations
- **Advanced Bracket Types**: Support for double elimination, round-robin, and Swiss tournaments
- **Seeding System**: Allow manual or automatic seeding of participants
- **Tournament Scheduling**: Time-based tournament progression and match scheduling

### User Experience

- **Mobile Responsiveness**: Optimize interface for mobile devices
- **Real-time Updates**: WebSocket integration for live tournament updates
- **Tournament History**: View and replay past tournaments
- **Export Functionality**: Export tournament results to PDF or CSV
- **Social Features**: Tournament sharing and spectator mode

### AI and Content

- **Custom AI Models**: Support for different AI providers and models
- **Prompt Categories**: Organize prompts by themes or difficulty levels
- **AI Judging**: Optional AI-powered match evaluation
- **Content Moderation**: Automated filtering of inappropriate content

### Performance and Scalability

- **Database Optimization**: Implement caching and query optimization
- **API Rate Limiting**: Protect against abuse and ensure fair usage
- **Horizontal Scaling**: Support for multiple server instances
- **Background Jobs**: Async processing for AI generation and heavy operations

### Analytics and Insights

- **Tournament Analytics**: Detailed statistics and performance metrics
- **Prompt Performance**: Track which prompts perform best across tournaments
- **User Engagement**: Analytics on voting patterns and participation
- **A/B Testing**: Framework for testing new features

## Documentation

- **API Documentation**: `backend/API_SUMMARY.md`
- **Testing Guide**: `backend/TESTING.md`
- **Frontend Guide**: `frontend/README.md`
