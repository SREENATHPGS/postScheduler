DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS posts;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    api_key TEXT NOT NULL,
    email TEXT NOT NULL,
    created TEXT DEFAULT (datetime('now', 'localtime')),
    updated TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    created TEXT NOT NULL,
    updated TEXT NOT NULL,
    media_link TEXT NOT NULL,
    media_story TEXT,
    user_id REFERENCES user(id),
    post_status TEXT DEFAULT 'saved',
    post_details JSON NOT NULL
    -- saved, scheduled, posted, published, failed
);