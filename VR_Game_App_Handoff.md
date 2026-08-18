# VR Game App — Project Handoff Document

**Prepared for:** VR Development Team  
**Tech Stack:** FastAPI (Backend) + MongoDB (Database) + VR Frontend  
**Auth:** JWT Bearer Token  

---

## 1. Roles

| Role | Description |
|------|-------------|
| superadmin | Manages users and assets. Created via seed + API. |
| user | Plays games, views leaderboard. Created by superadmin. |

---

## 2. Responsibility Split

### Backend Handles
- User creation, login, JWT token generation
- First login flag — forces password change on first login
- Storing all game session data (score, time, Q&A, boosters, gifts, etc.)
- Asset catalog management (name, gender, type, image, is_default)
- Tracking unlocked assets per user (permanently after gifted in skate session)
- Avatar equipped asset tracking per user per gender
- Leaderboard calculation (top 10 + current user rank) for both games
- Seeding superadmin

### VR Frontend Handles
- All player movement and controls
- Score, coins, health, time calculation during gameplay
- Booster logic during gameplay
- Question bank for both games (questions are stored in VR frontend)
- Sending final session data to backend on game end
- Attempt count management for Clean Deal (if time extended, increment attempt)
- Percentage calculation for Clean Deal
- On first login — redirect user to change password screen
- Equipping assets on avatar (call equip API after user selects)

---

## 3. Auth Flow

```
User opens app
    └── POST /auth/login  { emp_id, password }
            ├── is_first_login = true
            │       └── Frontend shows "Change Password" screen
            │               └── PATCH /auth/change-password
            │                       └── On success → proceed to home
            └── is_first_login = false
                    └── Returns token + user data + avatar data → Home screen
```

---

## 4. Skating Game — Flow

```
User starts Skating Game
    └── Selects mode: easy | medium | hard

During Game (all handled by VR frontend)
    ├── Player movement & controls
    ├── Score, coins, health tracking
    ├── Booster usage tracking (name + count)
    ├── Gift assets unlocked during session
    └── Q&A shown during game (20–25 questions from VR question bank)

Game Ends
    └── VR Frontend collects:
            ├── mode, score, coins, health, time
            ├── gifts[]       → asset IDs unlocked this session
            ├── boosters[]    → [ { name, count } ]
            └── test[]        → [ { question, answer, points } ]

    └── POST /skating/sessions  → Backend saves session
            └── Backend also permanently adds gifted assets to user's unlocked assets

Post Game
    ├── Show session summary to user
    └── User can view leaderboard → GET /leaderboard/skating
```

---

## 5. Clean Deal (Quiz Game) — Flow

```
User starts Clean Deal Game
    └── 5 minutes timer starts (handled by VR frontend)
    └── 7 stages, each stage has 3 questions (from VR question bank)

During Game (all handled by VR frontend)
    ├── Stage progression
    ├── Score and percentage calculation
    └── Timer tracking

Timer runs out before finishing
    └── Frontend shows: "Go Home" or "Extend Time"
            ├── Go Home → session ends, submit what is completed
            └── Extend Time → attempt count increments (attempt 2, 3, ...)
                    └── Frontend manages attempt number

Game Ends (all stages done or user exits)
    └── VR Frontend collects:
            ├── attempt (1, 2, 3...)
            ├── score, percentage, time_taken
            └── stages[] → [ { stage_number, questions: [ { question, answer, points } ] } ]

    └── POST /cleandeal/sessions → Backend saves session

Post Game
    ├── Show session summary to user
    └── User can view leaderboard → GET /leaderboard/cleandeal
```

---

## 6. Avatar & Assets Flow

```
User Creation (by superadmin)
    └── POST /users
            └── Backend auto-creates two avatar records (male + female)
                    └── Default assets assigned to both avatars from asset catalog

User views their avatar
    └── GET /users/{user_id}/avatar
            └── Returns both avatars with currently equipped assets

User unlocks new asset (via skate session gift)
    └── POST /skating/sessions  (gifts[] included)
            └── Backend adds gifted assets to unlocked_assets

User equips an asset
    └── PATCH /users/{user_id}/avatar/{gender}/equip  { asset_id }
            └── Asset must be default or already unlocked
            └── Backend updates equipped_assets on that avatar
```

---

## 7. API List

### Auth
| Method | Endpoint | Who Calls | Description |
|--------|----------|-----------|-------------|
| POST | /auth/login | VR Frontend | Login with emp_id + password. Returns token + user + avatar data |
| PATCH | /auth/change-password | VR Frontend (user) | Change password. Clears first login flag |

### User Management
| Method | Endpoint | Who Calls | Description |
|--------|----------|-----------|-------------|
| POST | /users | Superadmin panel | Create a new user |
| GET | /users | Superadmin panel | List all users |
| GET | /users/{user_id} | Superadmin / Self | Get user profile |
| PUT | /users/{user_id} | Superadmin panel | Update user details |
| DELETE | /users/{user_id} | Superadmin panel | Delete user and all data |

### Assets
| Method | Endpoint | Who Calls | Description |
|--------|----------|-----------|-------------|
| POST | /assets | Superadmin panel | Add new asset to catalog |
| GET | /assets | VR Frontend | Get all assets (filter by gender, type) |
| PUT | /assets/{asset_id} | Superadmin panel | Update asset |
| DELETE | /assets/{asset_id} | Superadmin panel | Delete asset |

### Avatar
| Method | Endpoint | Who Calls | Description |
|--------|----------|-----------|-------------|
| GET | /users/{user_id}/avatar | VR Frontend | Get user's avatars with equipped assets |
| PATCH | /users/{user_id}/avatar/{gender}/equip | VR Frontend (user) | Equip an asset on avatar |

### Unlocked Assets
| Method | Endpoint | Who Calls | Description |
|--------|----------|-----------|-------------|
| GET | /users/{user_id}/unlocked-assets | VR Frontend | Get all assets unlocked by user |

### Skating Game
| Method | Endpoint | Who Calls | Description |
|--------|----------|-----------|-------------|
| POST | /skating/sessions | VR Frontend (on game end) | Submit skate session data |
| GET | /skating/sessions/{user_id} | VR Frontend / Superadmin | Get all sessions of a user |
| GET | /skating/sessions/{user_id}/{session_id} | VR Frontend / Superadmin | Get full session detail |

### Clean Deal Game
| Method | Endpoint | Who Calls | Description |
|--------|----------|-----------|-------------|
| POST | /cleandeal/sessions | VR Frontend (on game end) | Submit clean deal session data |
| GET | /cleandeal/sessions/{user_id} | VR Frontend / Superadmin | Get all sessions of a user |
| GET | /cleandeal/sessions/{user_id}/{session_id} | VR Frontend / Superadmin | Get full session detail |

### Leaderboard
| Method | Endpoint | Who Calls | Description |
|--------|----------|-----------|-------------|
| GET | /leaderboard/skating | VR Frontend | Top 10 + current user rank (by best score, tie-break: latest session) |
| GET | /leaderboard/cleandeal | VR Frontend | Top 10 + current user rank (by best score, tie-break: latest session) |

### Seed
| Method | Endpoint | Who Calls | Description |
|--------|----------|-----------|-------------|
| POST | /seed/superadmin | Run once on server setup | Create initial superadmin account |

---

## 8. Key Rules & Notes

- **Assets** do not contain 3D files (no .glb / .fbx). Only name, gender, type, image, is_default.
- **Default assets** are assigned to every user's avatar at creation. No unlocking needed.
- **Unlockable assets** are only obtained through gifts in skate sessions. Once unlocked, permanent.
- **Booster data** is free-form (name + count). No fixed list in backend.
- **Question bank** lives in VR frontend. Backend only stores submitted question, answer, points.
- **Clean Deal attempts** are managed by VR frontend. Backend stores each attempt independently.
- **Percentage** for Clean Deal is calculated by VR frontend and sent to backend.
- **Score calculation** for both games is handled by VR frontend. Backend only stores.
- **Leaderboard** is global for both games. No per-mode or per-stage filtering.
- **First login** — user must change password before accessing the app.
