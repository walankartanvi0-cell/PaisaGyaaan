-- =========================================================
-- PAISAGYAAN
-- SQLITE DATABASE SCHEMA
-- =========================================================

PRAGMA foreign_keys = ON;


-- =========================================================
-- 1. USERS
-- =========================================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,

    email TEXT NOT NULL UNIQUE,

    password_hash TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 2. TRANSACTIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    transaction_type TEXT NOT NULL
        CHECK (
            transaction_type IN (
                'income',
                'expense',
                'investment'
            )
        ),

    amount REAL NOT NULL
        CHECK (amount > 0),

    category TEXT NOT NULL,

    transaction_date TEXT NOT NULL,

    note TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- =========================================================
-- 3. SAVINGS GOALS
-- =========================================================

CREATE TABLE IF NOT EXISTS savings_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    goal_name TEXT NOT NULL,

    target_amount REAL NOT NULL
        CHECK (target_amount > 0),

    target_date TEXT,

    current_amount REAL DEFAULT 0
        CHECK (current_amount >= 0),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- =========================================================
-- 4. LEARNING TOPICS
-- =========================================================

CREATE TABLE IF NOT EXISTS learning_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT NOT NULL,

    description TEXT,

    category TEXT NOT NULL,

    difficulty TEXT DEFAULT 'Beginner',

    content TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 5. QUIZ RESULTS
-- =========================================================

CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    topic_id INTEGER,

    score INTEGER NOT NULL DEFAULT 0,

    total_questions INTEGER NOT NULL DEFAULT 0,

    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (topic_id)
        REFERENCES learning_topics(id)
        ON DELETE SET NULL
);


-- =========================================================
-- 6. COMMUNITY POSTS
-- =========================================================

CREATE TABLE IF NOT EXISTS community_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    title TEXT NOT NULL,

    content TEXT NOT NULL,

    category TEXT DEFAULT 'General',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- =========================================================
-- 7. COMMUNITY COMMENTS
-- =========================================================

CREATE TABLE IF NOT EXISTS community_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    post_id INTEGER NOT NULL,

    user_id INTEGER NOT NULL,

    content TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (post_id)
        REFERENCES community_posts(id)
        ON DELETE CASCADE,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- =========================================================
-- 8. INDEXES
-- =========================================================

CREATE INDEX IF NOT EXISTS idx_transactions_user
ON transactions(user_id);


CREATE INDEX IF NOT EXISTS idx_transactions_date
ON transactions(transaction_date);


CREATE INDEX IF NOT EXISTS idx_goals_user
ON savings_goals(user_id);


CREATE INDEX IF NOT EXISTS idx_quiz_user
ON quiz_results(user_id);


CREATE INDEX IF NOT EXISTS idx_posts_user
ON community_posts(user_id);


CREATE INDEX IF NOT EXISTS idx_comments_post
ON community_comments(post_id);