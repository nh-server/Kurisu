-- Designed for PostgreSQL 10
-- This is still a work in progress and can change at any time!

DROP TABLE IF EXISTS attachments, actions_log, flags, no_filter, permanent_roles, staff, warns;

CREATE TABLE actions_log
(
  entry_id    BIGINT PRIMARY KEY,
  created_at  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  user_id     BIGINT,
  target_id   BIGINT,
  kind        INTEGER                  NOT NULL,
  description TEXT,
  extra       TEXT
);

CREATE TABLE attachments
(
  entry_id BIGINT REFERENCES actions_log (entry_id),
  url      TEXT
);

CREATE TABLE flags
(
  key   TEXT NOT NULL,
  value BOOLEAN
);

CREATE TABLE no_filter
(
  channel_id BIGINT NOT NULL
);

CREATE TABLE permanent_roles
(
  user_id BIGINT NOT NULL,
  role_id BIGINT
);

CREATE TABLE staff
(
  user_id BIGINT NOT NULL,
  level   TEXT
);

CREATE TABLE warns
(
  warn_id    BIGINT PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  user_id    BIGINT                   NOT NULL,
  issuer     BIGINT,
  reason     TEXT
)
