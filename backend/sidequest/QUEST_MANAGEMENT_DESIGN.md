# Quest Management System Design Document

## Overview

This document outlines the redesign of SideQuest's quest management system to implement a daily quest board concept with proper state management and lifecycle handling.

## Core Concepts

### Quest Board

- **Definition**: A daily collection of quests for a user that resets every 24 hours
- **Purpose**: Provides an abstraction layer for easily retrieving relevant quests for the current day
- **Lifecycle**: Generated fresh each day, cleaned up automatically when user requests their board

### Quest States

The system will use a single `status` field instead of multiple boolean columns:

1. **`potential`** - Quest is available for user to accept/decline
2. **`accepted`** - User has accepted the quest and is working on it
3. **`completed`** - User successfully completed the quest
4. **`failed`** - User accepted but failed to complete within time limit
5. **`abandoned`** - User accepted then later abandoned the quest
6. **`declined`** - User explicitly declined the quest (replaces current "skipped")

## Data Model Changes

### New QuestBoard Model

```python
class QuestBoard(db.Model):
    """Daily quest board for a user"""
    __table_args__ = {"schema": "sidequest"}
    __tablename__ = "sidequest_quest_boards"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Board metadata
    last_refreshed = db.Column(db.DateTime, nullable=False, default=db.func.now())
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now())

    # Relationships
    user = db.relationship("User", backref=db.backref("quest_boards", uselist=False))
    quests = db.relationship("SideQuest", backref="quest_board", lazy="dynamic")
```

### Updated SideQuest Model

```python
class SideQuest(db.Model):
    """Individual quest instances"""
    __table_args__ = {"schema": "sidequest"}
    __tablename__ = "sidequest_quests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quest_board_id = db.Column(db.Integer, db.ForeignKey("sidequest_quest_boards.id"), nullable=True)

    # Quest content (unchanged)
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.Enum(QuestCategory), nullable=False)
    estimated_time = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.Enum(QuestDifficulty), nullable=False)
    tags = db.Column(JSON, nullable=False, default=[])

    # NEW: Single status field replacing multiple booleans
    status = db.Column(db.Enum(QuestStatus), nullable=False, default=QuestStatus.POTENTIAL)

    # Completion details (unchanged)
    completed_at = db.Column(db.DateTime, nullable=True)
    feedback_rating = db.Column(db.Enum(QuestRating), nullable=True)
    feedback_comment = db.Column(db.Text, nullable=True)
    time_spent = db.Column(db.Integer, nullable=True)

    # Generation metadata (unchanged)
    generated_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    expires_at = db.Column(db.DateTime, nullable=False)
    model_used = db.Column(db.String(100), nullable=True)
    fallback_used = db.Column(db.Boolean, nullable=False, default=False)

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now())
```

### New QuestStatus Enum

```python
class QuestStatus(str, Enum):
    """Quest status states"""
    POTENTIAL = "potential"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"
    DECLINED = "declined"
```

## API Endpoints

### 1. Get Quest Board

```
GET /sidequest/quest-board
```

- **Purpose**: Retrieve user's current quest board
- **Logic**:
  - Check if board needs refresh (last_refreshed < today)
  - If refresh needed: clean up old board, generate new quests
  - Return current board with all quests
- **Response**: Quest board with quests organized by status

### 2. Update Quest Status

```
PUT /sidequest/quests/{quest_id}/status
```

- **Purpose**: Change quest status (accept, complete, abandon, etc.)
- **Validation**: Ensure valid state transitions
- **Response**: Updated quest data

### 3. Generate New Quest Board

```
POST /sidequest/quest-board/refresh
```

- **Purpose**: Force refresh of quest board (admin/debug use)
- **Logic**: Same as automatic refresh logic

## Quest Board Refresh Logic

### When Refresh is Triggered

- User requests quest board
- `last_refreshed` date is before current day (midnight check)

### Refresh Process

1. **Mark remaining potential quests as declined**
2. **Mark remaining accepted quests as failed**
3. **Remove all quests from current board** (set `quest_board_id = NULL`)
4. **Generate 3 new quests** with status `potential`
5. **Create new quest board** with current timestamp
6. **Associate new quests with new board**

### State Transition Rules

```
potential → accepted (user accepts)
potential → declined (user declines OR daily refresh)
accepted → completed (user completes)
accepted → abandoned (user abandons)
accepted → failed (daily refresh - time expired)
```

## Frontend Changes

### New Quest Board Screen

- **Single screen** with two tabs:
  - **Potential Tab**: Shows quests with status `potential`
  - **Active/Completed Tab**: Shows quests with status `accepted`, `completed`, `abandoned`

### Quest Actions

- **Potential Quests**: Accept, Decline buttons
- **Accepted Quests**: Complete, Abandon buttons
- **Completed Quests**: View feedback, no actions
- **Abandoned Quests**: "Pick Up Again" button (changes status back to `accepted`)

### Data Flow

1. App opens → Request quest board
2. Backend checks if refresh needed → Generates new board if necessary
3. Frontend receives quest board with organized quests
4. User interactions update quest status via API
5. UI updates to reflect new state

## Implementation Phases

### Phase 1: Backend Data Model

1. Create new `QuestBoard` model
2. Update `SideQuest` model with `status` field
3. Create database migration
4. Update existing quest generation logic

### Phase 2: Backend Logic

1. Implement quest board refresh logic
2. Update quest status endpoints
3. Add quest board retrieval endpoint
4. Update quest generation to work with new model

### Phase 3: Frontend Updates

1. Update quest types to use new status field
2. Create new Quest Board screen with tabs
3. Update quest actions to use new status API
4. Remove old boolean-based state logic

### Phase 4: Testing & Migration

1. Test new endpoints and logic
2. Migrate existing quest data to new status system
3. End-to-end testing of complete flow
4. Performance testing of board refresh logic

## Database Migration Strategy

### Migration Steps

1. **Add new columns**: `quest_board_id`, `status`
2. **Migrate existing data**: Convert boolean states to new status enum
3. **Create quest boards**: Generate quest boards for existing users
4. **Clean up old columns**: Remove `selected`, `completed`, `skipped` columns

### Data Preservation

- All existing quest data preserved
- Historical quests maintain their final state
- Analytics data remains intact

## Benefits of New Design

1. **Cleaner State Management**: Single status field instead of multiple booleans
2. **Daily Reset Logic**: Automatic cleanup without cron jobs
3. **Better User Experience**: Clear separation of potential vs. active quests
4. **Improved Analytics**: Better tracking of quest lifecycle
5. **Simplified Frontend**: Clearer data organization and display
6. **Scalability**: Easier to add new quest states in the future

## Risks & Considerations

1. **Data Migration**: Need careful migration of existing quest data
2. **Performance**: Board refresh logic needs to be efficient
3. **Timezone Handling**: Ensure consistent daily reset logic across timezones
4. **State Validation**: Ensure all status transitions are valid
5. **Backward Compatibility**: May need to maintain old endpoints during transition

## Success Metrics

1. **Quest Board Load Time**: < 500ms for board retrieval
2. **Status Update Response**: < 200ms for status changes
3. **Daily Reset Reliability**: 100% successful daily board refreshes
4. **User Experience**: Clear separation of quest states and actions
5. **Data Integrity**: No orphaned quests or invalid state transitions
