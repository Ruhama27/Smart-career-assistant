-- =============================================================================
-- PathFinder AI — Database Schema
-- Normalized SQLite schema for students, internships, skills, and applications
-- =============================================================================

PRAGMA foreign_keys = ON;

-- 1. Skills Lookup Table
CREATE TABLE IF NOT EXISTS skills (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL COLLATE NOCASE
);

-- 2. Students Table
CREATE TABLE IF NOT EXISTS students (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id    TEXT UNIQUE NOT NULL,
    name          TEXT NOT NULL,
    email         TEXT UNIQUE,
    university    TEXT,
    department    TEXT,
    year          INTEGER,
    cgpa          REAL,
    cgpa_scale    REAL DEFAULT 10.0,
    career_goal   TEXT,
    interests     TEXT,
    location_pref TEXT
);

-- 3. Student Skills (Normalized Many-to-Many)
CREATE TABLE IF NOT EXISTS student_skills (
    student_id  INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    skill_id    INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    proficiency TEXT DEFAULT 'beginner',
    PRIMARY KEY (student_id, skill_id)
);

-- 4. Internships Table
CREATE TABLE IF NOT EXISTS internships (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    internship_id TEXT UNIQUE NOT NULL,
    company       TEXT NOT NULL,
    role          TEXT NOT NULL,
    domain        TEXT,
    location      TEXT,
    is_remote     BOOLEAN DEFAULT FALSE,
    is_paid       BOOLEAN DEFAULT NULL,
    min_cgpa      REAL DEFAULT 0.0,
    cgpa_scale    REAL DEFAULT 10.0,
    duration      TEXT,
    deadline      DATE,
    source_url    TEXT,
    verified_at   DATETIME,
    is_active     BOOLEAN DEFAULT TRUE
);

-- 5. Internship Skills (Normalized Many-to-Many)
CREATE TABLE IF NOT EXISTS internship_skills (
    internship_id INTEGER NOT NULL REFERENCES internships(id) ON DELETE CASCADE,
    skill_id      INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    is_mandatory  BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (internship_id, skill_id)
);

-- 6. Ratings Table (Collaborative Filtering Data)
CREATE TABLE IF NOT EXISTS ratings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id    INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    internship_id INTEGER NOT NULL REFERENCES internships(id) ON DELETE CASCADE,
    rating        REAL NOT NULL,
    UNIQUE(student_id, internship_id)
);

-- 7. Saved Internships (Bookmarks)
CREATE TABLE IF NOT EXISTS saved_internships (
    student_id    INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    internship_id INTEGER NOT NULL REFERENCES internships(id) ON DELETE CASCADE,
    saved_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, internship_id)
);

-- 8. Applications Tracker
CREATE TABLE IF NOT EXISTS applications (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id    INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    internship_id INTEGER NOT NULL REFERENCES internships(id) ON DELETE CASCADE,
    status        TEXT DEFAULT 'Saved',
    applied_at    DATETIME,
    outcome_note  TEXT,
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- Compatibility & Query Views
-- Provides seamless DataFrame access matching legacy columns and formats
-- -----------------------------------------------------------------------------

CREATE VIEW IF NOT EXISTS v_students AS
SELECT
    s.id,
    s.student_id,
    s.name,
    s.email,
    s.university,
    s.university AS college,
    s.department,
    s.department AS branch,
    s.year,
    s.cgpa,
    s.cgpa_scale,
    s.career_goal,
    s.interests,
    s.location_pref,
    s.location_pref AS preferred_location,
    COALESCE(
        (SELECT GROUP_CONCAT(sk.name, ',')
         FROM student_skills ss
         JOIN skills sk ON ss.skill_id = sk.id
         WHERE ss.student_id = s.id), ''
    ) AS skills
FROM students s;

CREATE VIEW IF NOT EXISTS v_internships AS
SELECT
    i.id,
    i.internship_id,
    i.company,
    i.role,
    i.domain,
    i.location,
    i.is_remote,
    i.is_paid,
    i.min_cgpa,
    i.cgpa_scale,
    i.duration,
    i.deadline,
    i.source_url,
    i.verified_at,
    i.is_active,
    COALESCE(
        (SELECT GROUP_CONCAT(sk.name, ',')
         FROM internship_skills isk
         JOIN skills sk ON isk.skill_id = sk.id
         WHERE isk.internship_id = i.id), ''
    ) AS required_skills
FROM internships i;

CREATE VIEW IF NOT EXISTS v_ratings AS
SELECT
    r.id,
    s.student_id,
    i.internship_id,
    r.rating
FROM ratings r
JOIN students s ON r.student_id = s.id
JOIN internships i ON r.internship_id = i.id;
