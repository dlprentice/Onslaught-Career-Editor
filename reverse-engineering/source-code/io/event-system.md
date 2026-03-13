# Event System

## Event System (event.cpp/h, scheduledevent.cpp/h, eventmanager.cpp/h)

> Analysis added December 2025

**Purpose**: Time-based event scheduling and dispatch for the 20 FPS game loop. This system is purely runtime - **NOT persisted to save files**.

### Core Classes

The event system is built around three classes:

| Class | Purpose |
|-------|---------|
| `CEvent` | Base event with `mEventNum` (short) and `mToCall` (CActiveReader<CMonitor>) |
| `CScheduledEvent` | Extends CEvent, adds `mTime` for scheduling and `mData` for payload |
| `CEventManager` | Ring buffer scheduler, accessed via global singleton `EVENT_MANAGER` |

### Key Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `CLOCK_TICK` | 0.05f | 50ms per frame (20 FPS game loop) |
| `MAX_NUM_EVENTS` | 20000 | Pre-allocated event pool size |
| `NUM_EVENT_LIST_BUFFERS` | 200 | Ring buffer slots (10 seconds of frames) |
| `NUM_PRIORITY` | 3 | START/MIDDLE/END_OF_FRAME execution order |
| `NEXT_FRAME` | -1.0 | Magic value to schedule for next frame |

### Scheduling Mechanism

Events are scheduled using a ring buffer with overflow handling:

- **Events within 10 seconds**: Stored in the ring buffer with wrap-around index
- **Events beyond 10 seconds**: Stored in overflow buffer (time-sorted)
- **3 priority levels per frame**: Controls execution order within a frame

The ring buffer provides O(1) scheduling for near-future events (the common case), while the overflow buffer handles rare long-delay events.

### Event ID Ranges

Events are organized by class, each with a base offset:

| Class | Base | Example Events |
|-------|------|----------------|
| `EThingEvent` | 2000 | SHUTDOWN, START_DIE_PROCESS |
| `ActorEvent` | 3000 | MOVE, LF_MOVE |
| `EPlayerEvent` | 4000 | GOTO_CONTROL_VIEW |
| `EBattleEngineEvent` | 6000 | BECOME_JET, BECOME_WALKER |
| `EGameEvent` | 2000 | DEMO_RESTART_LEVEL, PAUSE_GAME |

### CActiveReader Safety Pattern

The event system uses `CActiveReader<CMonitor>` for safe event dispatch:

1. Target objects register listeners with the event system
2. When a target object dies, `ToReadDied()` is called, which nullifies the pointer
3. On event dispatch, `GetToCall()` is checked - if NULL, the event is silently skipped

This pattern prevents crashes from events targeting destroyed objects (a common source of bugs in game engines).

### Memory Pool

The event system uses a pre-allocated memory pool for efficiency:

- **20,000 events** pre-allocated at startup
- Free list linked via `mNextFreeSE` (union with `mTime` to save memory)
- `mBeingReused` flag prevents double-freeing during rapid allocation/deallocation cycles

This design avoids runtime heap allocation, which is critical for maintaining consistent frame timing.

### Relevance to Save Editing

**NONE** - Events are purely runtime state.

- A fresh event pool is created at level load
- No event data is serialized to .bes files
- Event scheduling state is discarded when the game exits

The event system is important for understanding game architecture and debugging, but has no impact on save file editing.

### Files Analyzed for This Section

| File | Purpose |
|------|---------|
| `event.cpp` | CEvent implementation |
| `event.h` | CEvent class definition |
| `scheduledevent.cpp` | CScheduledEvent implementation |
| `scheduledevent.h` | CScheduledEvent class definition, memory pool |
| `eventmanager.cpp` | CEventManager ring buffer implementation |
| `eventmanager.h` | CEventManager class definition, constants |

---

## Event Manager (EventManager.cpp/h)

Time-based event scheduling system for game logic.

**Key Constants:**
| Constant | Value | Notes |
|----------|-------|-------|
| `MAX_NUM_EVENTS` | 20000 | Maximum schedulable events |
| `NUM_EVENT_LIST_BUFFERS` | 200 | 10 seconds at 20fps |

**Architecture:**
- Circular buffer for near-future events
- Overflow list for far-future events
- Priority-based execution within frames

**Steam BEA.exe Mapping (verified):**

| Address | Name | Notes |
|---------|------|-------|
| 0x0044afe0 | `CEventManager__scalar_deleting_dtor` | MSVC scalar deleting dtor wrapper |
| 0x0044b000 | `CEventManager__dtor` | Calls `CEventManager__Shutdown` |
| 0x0044b060 | `CEventManager__Init` | Allocates overflow container + 20,000 event pool |
| 0x0044b1f0 | `CEventManager__Shutdown` | Clears ring/overflow state and frees pool |
| 0x0044b2a0 | `CEventManager__GetNextFreeEvent` | Pops event free-list head |
| 0x0044b2d0 | `CEventManager__AddEvent_TimeFromNow` | Relative-time AddEvent overload |
| 0x0044b310 | `CEventManager__AddEvent_ScheduledEvent` | Scheduled-event overload |
| 0x0044b370 | `CEventManager__AddEvent_AtTime` | Main scheduler (ring + overflow insertion) |
| 0x0044b5c0 | `CEventManager__Update` | Calls `AdvanceTime` then `Flush` |
| 0x0044b600 | `CEventManager__AdvanceTime` | Retail variant returns wrap flag while advancing |
| 0x0044b640 | `CEventManager__Flush` | Executes due events, cleans up free-list/reuse state |

Related scheduled-event helpers (mapped by callsite inference):

| Address | Name | Notes |
|---------|------|-------|
| 0x004de1f0 | `CScheduledEvent__Set` | Implements `Set(event_num, time, to_call, data)` (`mToCall`, `mData`, reuse flag) |
| 0x004de230 | `CScheduledEvent__dtor` | Destructor path: decrements static live counter and unregisters ActiveReader fields |

**Priority Levels:**
| Priority | Timing |
|----------|--------|
| `START_OF_FRAME` | Before physics |
| `MIDDLE_OF_FRAME` | During update |
| `END_OF_FRAME` | After rendering |

**Developer Comment:** "at the mo" (British slang for "at the moment")

**Typos Preserved:**
| Typo | Should Be |
|------|-----------|
| `schuled event` | scheduled event |
| `witch offset buffer` | which offset buffer |
| `previus_num_events_called` | previous_num_events_called |

---

## Active Reader System (activereader.cpp/h)

> Analysis added December 2025

The Active Reader system provides a runtime smart pointer/observer pattern for safely referencing game objects that can be destroyed during gameplay. **This is purely runtime memory management and has NO relevance to save files.**

### Purpose

In a game where objects can be destroyed at any time (enemies killed, buildings demolished, etc.), holding raw pointers to those objects creates a risk of dangling pointers. The Active Reader pattern provides:

1. **Safe object references** - Automatically detects when referenced objects are destroyed
2. **Null-on-delete semantics** - Pointers become NULL when their targets are destroyed
3. **Type-safe access** - Template class ensures correct typing

### Classes

| Class | Purpose |
|-------|---------|
| `CGenericActiveReader` | Base class with `mToRead` pointer and deletion callback |
| `CActiveReader<T>` | Template wrapper for type-safe access to objects of type T |

### How It Works

```
1. CActiveReader<CUnit> reader;      // Create smart pointer
2. reader.Set(someUnit);             // Point to a unit
      │
      ├── Register with CMonitor base class for deletion callbacks
      │
3. (gameplay happens)
      │
4. someUnit gets destroyed
      │
      ├── CMonitor shutdown/destructor logic nulls all registered reader cells (ToReadDied)
      │
      ▼
5. reader.mToRead = NULL             // Pointer safely nullified
      │
6. reader.Read() returns NULL        // Safe access, no crash
```

### Integration with CMonitor

The system requires referenced objects to inherit from `CMonitor`:

```cpp
// Conceptual - objects must be CMonitor-derived
class CUnit : public CMonitor { ... };

// When a CMonitor-derived object is destroyed, it notifies all readers:
CMonitor::~CMonitor() {
    // Notify all active readers that this object died
    for (each registered reader) {
        reader->ToReadDied();
    }
}
```

### Steam Build Mapping (BEA.exe)

The Steam PC port implements a functionally similar pattern (not assumed as source-identical), but in a very compact way:
- A `CGenericActiveReader` / `CActiveReader<T>` is often just the 4-byte **cell** that holds `mToRead`.
- The monitored object stores a deletion-event list pointer at `monitor + 0x04` (lazily allocated as a `CSPtrSet`).
- The deletion list stores pointers to reader cells; on monitor shutdown/destruction the engine nulls each cell (`*cell = NULL`), matching `ToReadDied()`.

Mapped helpers in the Steam build:
| Address | Name | Purpose |
|---------|------|---------|
| 0x00401000 | `CGenericActiveReader__SetReader` | Remove from old `mToRead+0x04`, assign, register with new monitor |
| 0x00401040 | `CMonitor__AddDeletionEvent` | Allocate/init `CSPtrSet` at `monitor+0x04` (if NULL) and add a reader cell |
| 0x0042d9b0 | `CMonitor__DeleteDeletionEvent` | Remove a reader cell from `monitor+0x04` deletion list when present |
| 0x0044b1d0 | `CGenericActiveReader__dtor` | Unregister helper (removes reader cell from `mToRead+0x04`) |
| 0x004bac40 | `CMonitor__Shutdown` | Monitor shutdown/destructor: iterate `monitor+0x04` and null each reader cell (`*cell = NULL`), then clear+free the `CSPtrSet` |

Binary-level details: `reverse-engineering/binary-analysis/functions/monitor.h/_index.md`

### Usage Throughout Codebase

Active Readers are used extensively for object references that may become invalid:

| Header File | Field | Type | Purpose |
|-------------|-------|------|---------|
| `BattleEngine.h` | `mUnit` | `CActiveReader<CUnit>` | Current target unit |
| `BattleEngine.h` | `mStandingOnThing` | `CActiveReader<CThing>` | Ground/platform reference |
| `BattleEngine.h` | `mAutoAimTarget` | `CActiveReader<CThing>` | Auto-aim lock target |
| `BattleEngine.h` | `mPlayer` | `CActiveReader<CPlayer>` | Owner player |
| `Camera.h` | `mForThing` | `CActiveReader<CThing>` | Camera focus target |
| `Player.h` | `mBattleEngine` | `CActiveReader<CBattleEngine>` | Player's battle engine |
| `event.h` | Event targets | `CActiveReader<*>` | Event dispatch targets |
| `scheduledevent.h` | Event data | `CActiveReader<*>` | Scheduled event references |

### Debug Integration

The system integrates with `CDXMemoryManager` for debug validation:

```cpp
#ifdef DEBUG
// Memory manager can validate active reader consistency
// Detect readers pointing to freed memory
// Track reader registration/deregistration
#endif
```

### Relevance to Save Editing

**NONE** - This is purely runtime memory management.

| Aspect | Save System | Active Reader System |
|--------|-------------|---------------------|
| **Persistence** | Written to .bes file | Never serialized |
| **Lifetime** | Survives game restart | Lost on level change |
| **Purpose** | Track player progress | Manage runtime references |
| **Data Location** | File offsets 0x0000-0x2714 | Only in RAM |

`CActiveReader` fields in structs are **transient** - they exist only while the game is running. When a save file is loaded, these pointers are re-established at runtime from the loaded game state, not from the save file itself.

### Why This Matters for RE

Understanding which struct fields are `CActiveReader<T>` helps identify:

1. **Transient vs persistent fields** - Reader fields are NOT saved
2. **Object relationships** - Shows what objects reference what
3. **Struct size accuracy** - Reader fields consume memory but not file space

When analyzing struct layouts, any field typed as `CActiveReader<*>` can be ignored for save file purposes.

### Files Analyzed for This Section

| File | Purpose |
|------|---------|
| `activereader.cpp` | Implementation of ToReadDied, registration |
| `activereader.h` | CGenericActiveReader and CActiveReader<T> template |

---
