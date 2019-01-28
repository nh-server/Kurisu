-- This is still a work in progress and can change at any time!

DROP TABLE IF EXISTS actions_log;
DROP TABLE IF EXISTS attachments;
DROP TABLE IF EXISTS flags;
DROP TABLE IF EXISTS no_filter;
DROP TABLE IF EXISTS restrictions;
DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS warns;

CREATE TABLE actions_log (
  entry_id INTEGER PRIMARY KEY,
  user_id INTEGER,
  target_id INTEGER,
  kind INTEGER,
  description TEXT,
  extra TEXT
);

CREATE TABLE attachments (
  entry_id INTEGER,
  url TEXT,
  FOREIGN KEY (entry_id) REFERENCES actions_log(entry_id)
);

CREATE TABLE flags (
  key TEXT NOT NULL,
  value INTEGER
);

CREATE TABLE no_filter (
  channel_id INTEGER NOT NULL
);

CREATE TABLE permanent_roles (
  user_id INTEGER NOT NULL,
  role_id INTEGER
);

CREATE TABLE staff (
  user_id INTEGER NOT NULL,
  level TEXT
);

CREATE TABLE mail_ignore (
  user_id INTEGER NOT NULL,
  reason TEXT
);
