-- ============================================
-- DOBRO DATABASE SCHEMA (SQLite-compatible)
-- ============================================

-- 1. Таблица auth_accounts (аккаунты пользователей)
CREATE TABLE IF NOT EXISTS auth_accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_type TEXT NOT NULL, -- 'volunteer' or 'organisation'
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_login TEXT,
    is_active INTEGER DEFAULT 1
);

-- 2. Таблица organisations (профили организаций)
CREATE TABLE IF NOT EXISTS organisations (
    organisation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    organisation_name TEXT NOT NULL,
    organisation_description TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    location TEXT,
    metadata TEXT DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES auth_accounts(account_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_organisations_account ON organisations(account_id);
CREATE INDEX IF NOT EXISTS idx_organisations_name ON organisations(organisation_name);

-- 3. Таблица volunteers (профили волонтёров)
CREATE TABLE IF NOT EXISTS volunteers (
    volunteer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    volunteer_name TEXT,
    volunteer_description TEXT,
    rating REAL DEFAULT 0.00,
    hours_total INTEGER DEFAULT 0,
    preferences TEXT DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES auth_accounts(account_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_volunteers_account ON volunteers(account_id);
CREATE INDEX IF NOT EXISTS idx_volunteers_name ON volunteers(volunteer_name);

-- 4. Таблица events (ивенты)
CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    organisation_id INTEGER NOT NULL,
    event_name TEXT NOT NULL,
    event_description TEXT,
    required_volunteers INTEGER DEFAULT 0,
    start_date TEXT NOT NULL,
    end_date TEXT,
    location TEXT,
    visibility TEXT CHECK (visibility IN ('public','private','unlisted')) DEFAULT 'public',
    metadata TEXT DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organisation_id) REFERENCES organisations(organisation_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_events_org ON events(organisation_id);
CREATE INDEX IF NOT EXISTS idx_events_date ON events(start_date);

-- 5. Таблица comments (комментарии)
CREATE TABLE IF NOT EXISTS comments (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER,
    organisation_id INTEGER,
    volunteer_id INTEGER,
    comment_text TEXT NOT NULL,
    rating INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
    FOREIGN KEY (organisation_id) REFERENCES organisations(organisation_id) ON DELETE CASCADE,
    FOREIGN KEY (volunteer_id) REFERENCES volunteers(volunteer_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_comments_event ON comments(event_id);
CREATE INDEX IF NOT EXISTS idx_comments_org ON comments(organisation_id);
CREATE INDEX IF NOT EXISTS idx_comments_volunteer ON comments(volunteer_id);

-- 6. Таблица requests (заявки волонтёров на ивенты)
CREATE TABLE IF NOT EXISTS requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    volunteer_id INTEGER NOT NULL,
    event_id INTEGER NOT NULL,
    status TEXT CHECK (status IN ('pending','accepted','rejected','cancelled')) DEFAULT 'pending',
    request_content TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (volunteer_id) REFERENCES volunteers(volunteer_id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
    UNIQUE (volunteer_id, event_id)
);

CREATE INDEX IF NOT EXISTS idx_requests_event_status ON requests(event_id, status);
CREATE INDEX IF NOT EXISTS idx_requests_volunteer_status ON requests(volunteer_id, status);

-- 7. Таблица activity_log (аудит действий)
CREATE TABLE IF NOT EXISTS activity_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    action TEXT NOT NULL,
    user_account INTEGER,
    payload TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_activity_entity ON activity_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_activity_time ON activity_log(created_at);

-- ============================================
-- === VIEW (представления) ===
-- ============================================

-- View: профиль волонтёра
CREATE VIEW IF NOT EXISTS view_volunteer_profile AS
SELECT v.volunteer_id,
       v.volunteer_name,
       v.volunteer_description,
       v.rating,
       v.hours_total,
       a.email AS account_email,
       (SELECT COUNT(*) FROM requests r WHERE r.volunteer_id = v.volunteer_id) AS requests_total,
       (SELECT COUNT(*) FROM comments c WHERE c.volunteer_id = v.volunteer_id) AS comments_total,
       v.preferences,
       v.created_at,
       v.updated_at
FROM volunteers v
JOIN auth_accounts a ON a.account_id = v.account_id;

-- View: краткое описание ивентов
CREATE VIEW IF NOT EXISTS view_event_summary AS
SELECT e.event_id,
       e.event_name,
       e.organisation_id,
       o.organisation_name,
       e.start_date,
       e.end_date,
       e.required_volunteers,
       (SELECT COUNT(*) FROM requests r WHERE r.event_id = e.event_id AND r.status = 'accepted') AS volunteers_confirmed,
       (SELECT COUNT(*) FROM requests r WHERE r.event_id = e.event_id) AS requests_total
FROM events e
LEFT JOIN organisations o ON o.organisation_id = e.organisation_id;

-- View: статистика ивентов по дням
CREATE VIEW IF NOT EXISTS view_event_daily_counts AS
SELECT date(start_date) AS day,
       organisation_id,
       COUNT(*) AS events_count
FROM events
GROUP BY day, organisation_id;

-- View: топ волонтёров по часам
CREATE VIEW IF NOT EXISTS view_top_volunteers AS
SELECT volunteer_id,
       volunteer_name,
       hours_total,
       rating
FROM volunteers
ORDER BY hours_total DESC;

-- ============================================
-- Конец схемы DOBRO (SQLite)
-- ============================================