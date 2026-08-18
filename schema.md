# VR Game App — Database Schema (Visual)

---

## 1. Users Collection

```
users
├── _id
├── username
├── emp_id        → unique employee ID
├── password (hashed)
├── role          → "superadmin" | "user"
├── is_first_login  → bool (triggers password change)
├── gender        → "male" | "female"
├── created_at
└── updated_at
```

---

## 2. Assets Collection (Predefined Catalog)

```
assets
├── _id
├── name
├── gender        → "male" | "female" | "unisex"
├── type          → "dress" | "gun" | "skate" | "wheels"
├── image         → (URL or filename)
├── is_default    → bool (default avatar assets vs unlockable)
└── created_at
```

---

## 3. Avatars Collection

```
avatars
├── _id
├── user_id       → ref: users._id
├── gender        → "male" | "female"
└── equipped_assets
    └── [ asset_id, ... ]   → ref: assets._id (currently wearing)
```

---

## 4. Unlocked Assets Collection

```
unlocked_assets
├── _id
├── user_id       → ref: users._id
├── asset_id      → ref: assets._id
└── unlocked_at
```

---

## 5. Skate Sessions Collection

```
skate_sessions
├── _id
├── user_id       → ref: users._id
├── mode          → "easy" | "medium" | "hard"
├── score
├── coins
├── health        → numeric
├── time          → seconds (duration)
├── played_at
├── gifts[]       → [ asset_id, ... ]  (assets unlocked this session)
├── boosters[]
│   ├── name
│   └── count
└── test[]
    ├── question
    ├── answer
    └── points
```

---

## 6. Clean Deal Sessions Collection

```
cleandeal_sessions
├── _id
├── user_id       → ref: users._id
├── attempt       → int (1, 2, 3, ... if time extended)
├── score
├── percentage
├── time_taken    → seconds
├── played_at
└── stages[]
    ├── stage_number  → 1 to 7
    └── questions[]
        ├── question
        ├── answer
        └── points
```

---

## Relationships Overview

```
users
 ├──< avatars           (one user → one avatar per gender, max 2)
 ├──< unlocked_assets   (one user → many unlocked assets)
 ├──< skate_sessions    (one user → many skate sessions)
 └──< cleandeal_sessions(one user → many clean deal sessions)

assets
 ├──< unlocked_assets   (one asset → unlocked by many users)
 └──  avatars.equipped_assets (assets worn by avatar)

skate_sessions.gifts → assets (assets unlocked in that session)

user_best_scores
 ├── user_id → ref: users._id
 └── one record per user per game_type (upserted on session submit)
```

---

## 7. User Best Scores Collection

```
user_best_scores
├── _id
├── user_id       → ref: users._id
├── game_type     → "skating" | "cleandeal"
├── best_score
├── session_id    → ref: skate_sessions._id or cleandeal_sessions._id
└── achieved_at   → timestamp when best score was first achieved
```

Index on: `(game_type, best_score DESC, achieved_at ASC)`

---

## Leaderboard Logic

```
On every session submit (skating or cleandeal)
 └── Always save session document
 └── Upsert into user_best_scores:
         ├── new score > current best  → update best_score + achieved_at
         ├── new score = current best  → do nothing (keep original achieved_at)
         └── new score < current best  → do nothing

Skate Leaderboard  →  GET /leaderboard/skating
 └── Query: user_best_scores where game_type = "skating"
     → sort: best_score DESC, achieved_at ASC
     → top 10 + current user rank

Clean Deal Leaderboard  →  GET /leaderboard/cleandeal
 └── Query: user_best_scores where game_type = "cleandeal"
     → sort: best_score DESC, achieved_at ASC
     → top 10 + current user rank

Current User Rank
 └── count(user_best_scores where game_type = X and best_score > current_user_best) + 1
     → if user has never played → current_user: null

Tie-break Rule
 └── Same score → earlier achieved_at wins (first to reach that score ranks higher)
```

---

## Auth Flow

```
POST /auth/login
 └── is_first_login = true?
     ├── YES → return token + flag → frontend redirects to change password
     └── NO  → return token + user data + avatar data
```
