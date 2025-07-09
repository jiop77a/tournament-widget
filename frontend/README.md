# Tournament Widget Frontend

React-based frontend for the Tournament Widget application, built with TypeScript, Vite, and Material-UI.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:5173
```

## Development

### Available Scripts

```bash
npm run dev          # Start development server (http://localhost:5173)
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run lint:fix     # Fix ESLint issues automatically
npm run test         # Run tests in watch mode
npm run test:run     # Run tests once
npm run test:coverage # Run tests with coverage report
```

### Testing

The frontend uses **Vitest** for testing with comprehensive test utilities:

```bash
# Run all tests
npm run test:run

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode (development)
npm run test
```

**Test Structure:**
- `src/components/__tests__/` - Component tests
- `src/services/__tests__/` - Service layer tests  
- `src/utils/__tests__/` - Utility function tests
- `src/test/` - Test utilities and setup

**Current Coverage:**
- **API Service**: 77% coverage
- **Test Utilities**: 100% coverage
- **Config Utilities**: 100% coverage
- **NavigationHeader**: 100% coverage
- **TournamentCreationForm**: 56% coverage

### Code Quality

**ESLint Configuration:**
- TypeScript-aware linting
- React hooks rules
- React refresh rules
- Automatic formatting on save

**TypeScript:**
- Strict type checking enabled
- Path aliases configured (`@/` for `src/`)
- Separate configs for app and tests

### Build Optimization

The build is optimized with **chunk splitting** for better caching:

```bash
npm run build
```

**Output chunks:**
- `react` - React core libraries (~12KB)
- `router` - React Router (~34KB)  
- `mui` - Material-UI components (~284KB)
- `index` - Application code (~202KB)

This ensures vendor libraries are cached separately from application code.

## Architecture

### Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Material-UI v6** - Component library
- **React Router v7** - Client-side routing
- **Vitest** - Testing framework
- **ESLint** - Code linting

### Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── __tests__/      # Component tests
│   │   ├── NavigationHeader.tsx
│   │   ├── TournamentCreationForm.tsx
│   │   └── ...
│   ├── pages/              # Page components
│   │   ├── HomePage.tsx
│   │   ├── TournamentBracketPage.tsx
│   │   └── ...
│   ├── services/           # API and external services
│   │   ├── __tests__/      # Service tests
│   │   └── api.ts
│   ├── hooks/              # Custom React hooks
│   │   └── useTournament.ts
│   ├── utils/              # Utility functions
│   │   ├── __tests__/      # Utility tests
│   │   └── config.ts
│   ├── types/              # TypeScript type definitions
│   │   ├── api.ts
│   │   ├── tournament.ts
│   │   └── index.ts
│   ├── test/               # Test utilities and setup
│   │   ├── setup.ts
│   │   ├── utils.ts
│   │   ├── mockUtils.ts
│   │   ├── renderUtils.tsx
│   │   └── TestProvider.tsx
│   ├── App.tsx             # Main app component
│   └── main.tsx            # Application entry point
├── public/                 # Static assets
├── dist/                   # Build output (generated)
├── package.json            # Dependencies and scripts
├── vite.config.ts          # Vite configuration
├── tsconfig.json           # TypeScript configuration
├── eslint.config.js        # ESLint configuration
└── README.md               # This file
```

### Key Components

**Core Components:**
- `TournamentCreationForm` - Create new tournaments
- `TournamentBracket` - Display tournament bracket
- `MatchVoting` - Vote on individual matches
- `NavigationHeader` - Breadcrumb navigation

**Display Components:**
- `TournamentWinner` - Show tournament results
- `MatchCard` - Individual match display
- `ByeCard` - Bye round indicator
- `VotingOption` - Voting button component

**Pages:**
- `HomePage` - Landing page and tournament creation
- `TournamentBracketPage` - Tournament overview and bracket
- `MatchVotingPage` - Individual match voting

### API Integration

The frontend communicates with the Flask backend via REST API:

```typescript
// API service with automatic error handling
import { apiService } from './services/api';

// Create tournament
const tournament = await apiService.createTournament(data);

// Get tournament status  
const status = await apiService.getTournamentStatus(id);

// Submit vote
await apiService.submitVote(matchId, winner);
```

**Configuration:**
- API base URL configurable via `VITE_API_BASE_URL` environment variable
- Defaults to `http://localhost:5001/api` for development
- Automatic JSON parsing and error handling

## Environment Configuration

Create a `.env` file in the project root (not frontend folder) for shared configuration:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:5001/api

# Development
VITE_DEV_MODE=true
```

**Environment Variables:**
- `VITE_API_BASE_URL` - Backend API base URL
- All Vite env vars must be prefixed with `VITE_`

## Contributing

### Development Workflow

1. **Start the backend** (see main README)
2. **Start the frontend**: `npm run dev`
3. **Make changes** with hot reload
4. **Run tests**: `npm run test:run`
5. **Check linting**: `npm run lint`
6. **Build**: `npm run build`

### Adding Tests

When adding new components or features:

1. **Create test files** in appropriate `__tests__/` directory
2. **Use test utilities** from `src/test/`
3. **Follow existing patterns** (see `NavigationHeader.test.tsx`)
4. **Run coverage**: `npm run test:coverage`

### Code Style

- **TypeScript**: Use strict typing, avoid `any`
- **Components**: Functional components with hooks
- **Testing**: Focus on user behavior, not implementation
- **Imports**: Use absolute imports with `@/` alias when helpful

## Troubleshooting

**Common Issues:**

- **Port conflicts**: Frontend runs on 5173, backend on 5001
- **API errors**: Check backend is running and CORS is configured
- **Build errors**: Clear `node_modules` and reinstall
- **Test timeouts**: Check for infinite loops in async tests

**Performance:**
- Use React DevTools for component debugging
- Check Network tab for API call timing
- Use Lighthouse for performance auditing
