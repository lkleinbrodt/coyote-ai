# SideQuest Backend Package

## Overview

The SideQuest backend provides a complete API for quest generation, user management, and quest lifecycle management. It integrates with OpenAI for intelligent quest generation and includes a robust fallback system.

## Quick Start

### Environment Variables

```bash
export OPENAI_API_KEY="your_openai_api_key"
export PING_DB_API_KEY="your_ping_db_key"
```

### API Base URL

`/api/sidequest`

## Core Components

### Models (`models.py`)

- **`SideQuestUser`**: User preferences and settings
- **`SideQuest`**: Individual quest instances
- **`QuestGenerationLog`**: Analytics and monitoring

### Services (`services.py`)

- **`QuestGenerationService`**: AI-powered quest generation with fallbacks
- **`UserService`**: User profile management
- **`QuestService`**: Quest lifecycle operations

### Routes (`routes.py`)

- User preferences and onboarding
- Quest generation and management
- Analytics and history

## Key Features

✅ **AI-Powered Quest Generation** - OpenAI GPT-4 integration  
✅ **Fallback System** - Curated quests when AI unavailable  
✅ **User Personalization** - Category preferences, difficulty, time constraints  
✅ **Quest Lifecycle** - Select, complete, skip with feedback  
✅ **Analytics** - Comprehensive logging and performance tracking  
✅ **JWT Authentication** - Secure user-specific endpoints

## API Endpoints

| Endpoint                | Method  | Description                 |
| ----------------------- | ------- | --------------------------- |
| `/health`               | GET     | Service health check        |
| `/preferences`          | GET/PUT | User preferences management |
| `/generate`             | POST    | Generate daily quests       |
| `/quests`               | GET     | Get user's quests           |
| `/quests/{id}/select`   | POST    | Select a quest              |
| `/quests/{id}/complete` | POST    | Complete a quest            |
| `/quests/{id}/skip`     | POST    | Skip a quest                |
| `/history`              | GET     | Get quest history           |
| `/onboarding/complete`  | POST    | Complete onboarding         |

## Database Schema

The package creates three main tables:

- `sidequest_users` - User preferences and settings
- `sidequest_quests` - Individual quest instances
- `sidequest_generation_logs` - Analytics and monitoring

## Testing

Run the simple tests to verify core functionality:

```bash
python3 -m pytest tests/test_sidequest_simple.py -v
```

## Production Deployment

1. Set required environment variables
2. Ensure database migrations are run
3. Verify OpenAI API access
4. Configure logging and monitoring

## Architecture

```
API Routes → Service Layer → Database/LLM
(routes.py)  (services.py)   (models.py)
```

Clean separation of concerns with Flask Blueprint architecture.

## Status

✅ **Implementation Complete** - Production ready  
🚧 **Testing** - Core tests passing, full app testing needs configuration  
🎯 **Next Phase** - Frontend integration and deployment

---

For detailed implementation information, see `SideQuest-Backend-Summary.md` in the project root.
