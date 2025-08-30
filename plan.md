# Character Similarity Explorer Implementation Plan

## Overview

This plan outlines the step-by-step implementation of a Character Similarity Explorer feature for the coyote-ai application. The feature will allow users to search for literary characters and find similar characters based on their dialogue patterns and personality traits.

## Phase 1: Backend Foundation & Database Setup ✅ COMPLETED

### Step 1.1: Update `requirements.txt` ✅ COMPLETED

**Implementation**: Added necessary dependencies for vector operations and embeddings.

- Added `sentence-transformers==3.0.1` for generating text embeddings
- Added `numpy==1.26.4` for numerical operations
- Added `pgvector==0.2.4` for PostgreSQL vector extension

**Files Modified**: `backend/requirements.txt`

### Step 1.2: Add Vector Configuration to `config.py` ✅ COMPLETED

**Implementation**: Added configuration for embedding models and dimensions.

- Added `EMBEDDING_MODEL = "all-MiniLM-L6-v2"` (384 dimensions)
- Added `EMBEDDING_DIMENSION = 384`
- Added `DIALOGUE_EXTRACTION_MODEL = "anthropic/claude-3-haiku"`

**Files Modified**: `backend/config.py`

### Step 1.3: Create Database Models ✅ COMPLETED

**Implementation**: Created SQLAlchemy models for the character explorer feature.

- Created `Book` model with title, author, total_characters, and timestamps
- Created `Character` model with name, total_quotes, embedding, and book relationship
- Created `Quote` model with text, embedding, word_count, and character relationship
- Created `CharacterSimilarity` model for storing similarity scores
- Used `pgvector.sqlalchemy.Vector` for embedding storage

**Files Created**: `backend/character_explorer/models.py`

### Step 1.4: Generate and Apply Database Migration ✅ COMPLETED

**Implementation**: Created and applied database migration for the new schema.

- Generated migration with `flask db migrate -m "Add character explorer models and vector extension"`
- Applied migration with `flask db upgrade`
- Added schema creation and pgvector extension setup
- Fixed Vector import issues in migration file

**Files Modified**: `migrations/versions/3dc3c1866500_add_character_explorer_models_and_.py`

## Phase 2: Data Ingestion Pipeline ✅ COMPLETED

### Step 2.1: Create the Embedding Service ✅ COMPLETED

**Implementation**: Built service for generating vector embeddings.

- Created `EmbeddingService` class with sentence-transformers
- Implemented `generate_quote_embedding()` for individual quotes
- Implemented `generate_character_embedding()` for character centroids
- Added proper error handling and logging

**Files Created**: `backend/character_explorer/services/embedding_service.py`

### Step 2.2: Create the Dialogue Extraction Service ✅ COMPLETED

**Implementation**: Built service for extracting dialogue from book text using LLM.

- Created `DialogueExtractor` class with OpenRouter integration
- Implemented text chunking for large books
- Added JSON response parsing with error handling
- Implemented filtering for quality quotes (minimum 10 words)

**Files Created**: `backend/character_explorer/services/dialogue_extractor.py`

### Step 2.3: Create an Ingestion Command ✅ COMPLETED

**Implementation**: Built Flask CLI command for orchestrating the ingestion pipeline.

- Created `ingest_book_command` with Click integration
- Added automatic metadata extraction from book text
- Implemented duplicate book detection and force re-ingestion
- Added comprehensive logging and progress feedback
- Integrated all services (dialogue extraction, embedding generation, database storage)

**Files Created**: `backend/character_explorer/ingest.py`

## Phase 3: Backend API Development ✅ COMPLETED

### Step 3.1: Create the Character Service ✅ COMPLETED

**Implementation**: Built business logic service for character operations.

- Created `CharacterService` class with database operations
- Implemented character search with fuzzy matching
- Added random character selection
- Built similar character finding using vector distance
- Added representative quotes retrieval

**Files Created**: `backend/character_explorer/services/character_service.py`

### Step 3.2: Create API Routes ✅ COMPLETED

**Implementation**: Created Flask API endpoints for the character explorer.

- Created `character_explorer_bp` blueprint
- Added search endpoint: `GET /character-explorer/search`
- Added random character endpoint: `GET /character-explorer/random`
- Added similar characters endpoint: `GET /character-explorer/<id>/similar`
- Added character quotes endpoint: `GET /character-explorer/<id>/quotes`
- Added books list endpoint: `GET /character-explorer/books`
- Implemented JWT authentication and error handling

**Files Created**: `backend/character_explorer/routes.py`

### Step 3.3: Register the Blueprint and CLI Command ✅ COMPLETED

**Implementation**: Integrated the new blueprint and command into the main Flask app.

- Added imports for `character_explorer_bp` and `ingest_book_command`
- Registered blueprint with `api_bp`
- Registered CLI command with `app.cli`
- Added model imports to ensure Alembic can detect them

**Files Modified**: `backend/__init__.py`

## Phase 4: Frontend Development ✅ COMPLETED

### Step 4.1: Add New Page Route ✅ COMPLETED

**Implementation**: Added routing for the character explorer page.

- Added lazy-loaded route in `App.tsx`
- Added route to `VALID_REDIRECT_PATHS` in `routes.ts`
- Implemented proper TypeScript routing

**Files Modified**:

- `frontend/src/App.tsx`
- `frontend/src/utils/routes.ts`

### Step 4.2: Create API Service and Types ✅ COMPLETED

**Implementation**: Created TypeScript interfaces and API service functions.

- Defined `Book`, `Character`, `Quote`, and `SimilarCharacter` interfaces
- Created `characterExplorerApi` service with axios integration
- Implemented all API endpoint functions with proper typing
- Added error handling and response validation

**Files Created**:

- `frontend/src/character_explorer/types.ts`
- `frontend/src/character_explorer/services/api.ts`

### Step 4.3: Build Frontend Components ✅ COMPLETED

**Implementation**: Created React components for the character explorer UI.

- Built `CharacterSearch` component with Command/Popover UI
- Created `SimilarCharactersList` component with Card/Badge display
- Implemented `CharacterQuotes` component with quote display
- Used Shadcn UI components for consistent styling
- Added loading states and error handling

**Files Created**:

- `frontend/src/character_explorer/components/CharacterSearch.tsx`
- `frontend/src/character_explorer/components/SimilarCharactersList.tsx`
- `frontend/src/character_explorer/components/CharacterQuotes.tsx`

### Step 4.4: Assemble the Main Page ✅ COMPLETED

**Implementation**: Created the main character explorer page component.

- Built `CharacterExplorerPage` with state management
- Integrated all child components
- Implemented data fetching and error handling
- Added loading states and user feedback
- Created responsive layout with proper styling

**Files Created**: `frontend/src/character_explorer/pages/CharacterExplorerPage.tsx`

## Phase 5: Finalization & Polish

### Step 5.1: Update Dialogue Extractor with Structured Outputs ✅ COMPLETED

**Implementation**: Enhanced dialogue extraction with OpenAI structured outputs.

- Updated model from `anthropic/claude-3-haiku` to `openai/gpt-4o-mini`
- Implemented JSON schema validation with `response_format`
- Added structured output schema for reliable parsing
- Improved error handling and response validation
- Enhanced prompt for better dialogue extraction

**Files Modified**: `backend/character_explorer/services/dialogue_extractor.py`

### Step 5.2: Add Landing Page Link

**Implementation**: Add navigation link to the character explorer on the landing page.

- Add link in the navigation menu
- Update any relevant UI components

**Files to Modify**: `frontend/src/pages/Landing.tsx`

### Step 5.3: Test the API Endpoints

**Implementation**: Comprehensive testing of all backend endpoints.

- Test search functionality
- Test random character selection
- Test similar character finding
- Test quote retrieval
- Test error handling and edge cases

### Step 5.4: Test the Frontend UI

**Implementation**: End-to-end testing of the frontend interface.

- Test character search and selection
- Test similar character display
- Test quote viewing
- Test responsive design
- Test error states and loading

### Step 5.5: Run Ingestion on Sample Book

**Implementation**: Test the complete ingestion pipeline.

- Download a sample book (e.g., Emma from Project Gutenberg)
- Run the ingestion command
- Verify data quality and completeness
- Test the full user experience

### Step 5.6: Code Review and Optimization

**Implementation**: Final code review and performance optimization.

- Review code quality and consistency
- Optimize database queries
- Improve error handling
- Add comprehensive logging
- Performance testing and optimization

## Current Progress Summary

✅ **Completed Phases**: 1, 2, 3, 4, and Step 5.1
🔄 **In Progress**: Phase 5 (Finalization & Polish)
⏳ **Remaining**: Steps 5.2-5.6

### Key Achievements:

- **Backend Foundation**: Complete database setup with vector support
- **Data Pipeline**: Full ingestion system with automatic metadata extraction
- **API Development**: Complete REST API with all necessary endpoints
- **Frontend**: Complete React interface with modern UI components
- **Enhanced Extraction**: Structured outputs for more reliable dialogue parsing

### Next Steps:

1. Add landing page navigation link
2. Comprehensive testing of API and frontend
3. Sample book ingestion and validation
4. Final code review and optimization

The core functionality is now implemented! You can:

1. **Test the backend** by running the Flask app and testing the API endpoints
2. **Test the frontend** by running the React app and navigating to `/character-explorer`
3. **Ingest a book** using the CLI command: `flask ingest-book /path/to/book.txt`
4. **Use structured outputs** for more reliable dialogue extraction with OpenAI models
