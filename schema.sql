
PRAGMA application_id = 0x4B757269;
PRAGMA user_version = 0x55566572;

create table friend_codes
(
  user_id INTEGER PRIMARY KEY,
  fc      INTEGER
);

create table helpers
(
  user_id INTEGER PRIMARY KEY,
  console text
);

create table nofilter
(
  channel_id INTEGER PRIMARY KEY
);

create table permanent_roles
(
  user_id int,
  role_id integer
);

create table softbans
(
  user_id   INTEGER PRIMARY KEY,
  issuer_id int,
  reason    text,
  timestamp text
);

create table staff
(
  user_id  INTEGER PRIMARY KEY,
  position TEXT
);

create table timed_restrictions
(
  user_id   integer,
  timestamp TEXT,
  type      text,
  alert     integer default 0
);

create table warns
(
  warn_id   INTEGER PRIMARY KEY,  
  user_id   int,
  issuer_id int,
  reason    text
);

create table watchlist
(
  user_id INTEGER PRIMARY KEY
);

create table wordfilter
(
  word     TEXT PRIMARY KEY,
  kind     TEXT
);

create table flags
(
  name     TEXT PRIMARY KEY,
  value    TINYINT default 0
);

