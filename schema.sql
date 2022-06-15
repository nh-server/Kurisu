create table approvedinvites
(
	code TEXT PRIMARY KEY,
	uses INTEGER NOT NULL DEFAULT 0,
	alias TEXT NOT NULL
);


create table channels
(
	id BIGINT PRIMARY KEY,
	name TEXT NOT NULL,
	filtered BOOLEAN NOT NULL DEFAULT TRUE,
	lock_level INTEGER NOT NULL DEFAULT 0,
	mod_channel BOOLEAN NOT NULL DEFAULT FALSE
);


create table filteredwords
(
	word TEXT PRIMARY KEY,
	kind TEXT NOT NULL
);


create table flags
(
	name TEXT PRIMARY KEY,
	value BOOLEAN NOT NULL
);


create table levenshteinwords
(
	word TEXT NOT NULL PRIMARY KEY,
	threshold INTEGER NOT NULL,
	kind TEXT NOT NULL,
	whitelisted BOOLEAN NOT NULL DEFAULT FALSE
);


create table members
(
	id BIGINT PRIMARY KEY,
	watched BOOLEAN NOT NULL DEFAULT FALSE
);

create table linkedmembers
(
    user_id BIGINT NOT NULL REFERENCES members(id),
    user_id2 BIGINT NOT NULL REFERENCES members(id),
    PRIMARY KEY (user_id, user_id2)
);


create table friendcodes
(
	user_id BIGINT PRIMARY KEY REFERENCES members(id),
	fc_3ds BIGINT UNIQUE,
	fc_switch BIGINT UNIQUE
);


create table reminders
(
	id BIGINT PRIMARY KEY,
	reminder_date TIME WITH TIME ZONE NOT NULL ,
	author_id BIGINT NOT NULL REFERENCES members(id),
	content TEXT NOT NULL
);


create table roles
(
	id BIGINT PRIMARY KEY,
	name TEXT NOT NULL
);


create table permanentroles
(
	user_id BIGINT NOT NULL REFERENCES members(id),
	role_id BIGINT NOT NULL REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);


create table rules
(
	id INTEGER PRIMARY KEY,
	description TEXT NOT NULL
);


create table softbans
(
	id BIGINT PRIMARY KEY,
	user_id BIGINT NOT NULL REFERENCES members(id),
	issuer_id BIGINT NOT NULL REFERENCES members(id),
	reason TEXT NOT NULL,
    UNIQUE (user_id)
);


create table staff
(
	user_id BIGINT PRIMARY KEY REFERENCES members(id),
	position TEXT NOT NULL,
	console TEXT
);


create table tags
(
	id BIGINT PRIMARY KEY,
	title TEXT NOT NULL,
	content TEXT NOT NULL,
	author_id BIGINT NOT NULL REFERENCES members(id),
	UNIQUE (title)
);


create table restrictions
(
	id BIGINT PRIMARY KEY,
	user_id BIGINT NOT NULL REFERENCES members(id),
	type TEXT NOT NULL,
	end_date TIME WITH TIME ZONE,
	alerted BOOLEAN NOT NULL DEFAULT FALSE,
	UNIQUE (user_id, type)
);


create table timedroles
(
	id BIGINT PRIMARY KEY,
	role_id BIGINT NOT NULL,
	user_id BIGINT NOT NULL REFERENCES members(id),
	expiring_date TIME WITH TIME ZONE NOT NULL,
	UNIQUE (role_id, user_id)
);


create table warns
(
	id BIGINT PRIMARY KEY,
	user_id BIGINT NOT NULL REFERENCES members(id),
	issuer_id BIGINT NOT NULL REFERENCES members(id),
	reason TEXT
);


create table whitelistedwords
(
	word TEXT PRIMARY KEY
);


create table citizens
(
	id BIGINT PRIMARY KEY references members(id),
	social_credit INTEGER NOT NULL DEFAULT 0
);


create table voteviews
(
	id BIGINT PRIMARY KEY,
	message_id BIGINT NOT NULL,
	identifier TEXT NOT NULL,
	author_id BIGINT NOT NULL,
	options TEXT NOT NULL,
	start TIME WITH TIME ZONE NOT NULL,
	staff_only BOOLEAN NOT NULL
);


create table votes
(
	view_id BIGINT NOT NULL REFERENCES voteviews(id) ON DELETE CASCADE,
	voter_id BIGINT NOT NULL,
	option TEXT NOT NULL,
    PRIMARY KEY (view_id, voter_id)
);


create table changedroles
(
	channel_id BIGINT NOT NULL REFERENCES channels(id),
	role_id BIGINT NOT NULL,
	original_value BOOLEAN,
    PRIMARY KEY (channel_id, role_id)
);


