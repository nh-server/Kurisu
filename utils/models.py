from gino import Gino

db = Gino()


class Staff(db.Model):
    __tablename__ = "staff"
    id = db.Column(db.BigInteger, db.ForeignKey("members.id"), primary_key=True)
    position = db.Column(db.String(8))
    console = db.Column(db.String(8))


class Warn(db.Model):
    __tablename__ = "warns"
    id = db.Column(db.BigInteger(), primary_key=True)
    user = db.Column(db.BigInteger(), db.ForeignKey("members.id"))
    issuer = db.Column(db.BigInteger(), db.ForeignKey("members.id"))
    reason = db.Column(db.Unicode())


class FriendCode(db.Model):
    __tablename__ = "friendcodes"
    id = db.Column(db.BigInteger, db.ForeignKey("members.id"), primary_key=True)
    fc_3ds = db.Column(db.BigInteger, default=None)
    fc_switch = db.Column(db.BigInteger, default=None)


class Channel(db.Model):
    __tablename__ = "channels"
    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.Unicode)
    private = db.Column(db.Boolean(), default=False)
    mod_channel = db.Column(db.Boolean(), default=False)
    default_role = db.Column(db.BigInteger(), db.ForeignKey("roles.id"), default=None)
    lock_level = db.Column(db.Integer, default=0)
    nofilter = db.Column(db.Boolean(), default=False)

    @property
    def is_mod_channel(self):
        return self.mod_channel


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.Unicode)


class PermanentRole(db.Model):
    __tablename__ = "permanentroles"
    user_id = db.Column(db.BigInteger(), db.ForeignKey("members.id"))
    role_id = db.Column(db.BigInteger(), db.ForeignKey("roles.id"))
    _pk = db.PrimaryKeyConstraint('user_id', 'role_id', name='permanentroles_pkey')


class TimedRestriction(db.Model):
    __tablename__ = "timed_restriction"
    id = db.Column(db.BigInteger(), primary_key=True)
    user = db.Column(db.BigInteger, db.ForeignKey("members.id"))
    type = db.Column(db.String(12))
    end_date = db.Column(db.DateTime())
    alerted = db.Column(db.Boolean(), default=False)


class TimedRole(db.Model):
    __tablename__ = "timedroles"
    id = db.Column(db.BigInteger(), primary_key=True)
    role_id = db.Column(db.BigInteger(), db.ForeignKey("roles.id"))
    user_id = db.Column(db.BigInteger, db.ForeignKey("members.id"))
    expiring_date = db.Column(db.DateTime())


class Member(db.Model):
    __tablename__ = "members"
    id = db.Column(db.BigInteger(), primary_key=True)
    watched = db.Column(db.Boolean(), default=False)


class Softban(db.Model):
    __tablename__ = "softbans"
    id = db.Column(db.BigInteger(), primary_key=True)
    user = db.Column(db.BigInteger(), db.ForeignKey("members.id"))
    issuer = db.Column(db.BigInteger(), db.ForeignKey("members.id"))
    reason = db.Column(db.Unicode())


class Flag(db.Model):
    __tablename__ = "flags"
    name = db.Column(db.String(20), primary_key=True)
    value = db.Column(db.Boolean(), default=False)


class FilteredWord(db.Model):
    __tablename__ = "filteredwords"
    word = db.Column(db.String(), primary_key=True)
    kind = db.Column(db.String())


class LevenshteinWord(db.Model):
    __tablename__ = "levenshteinwords"
    word = db.Column(db.String(), primary_key=True)
    threshold = db.Column(db.Integer())
    kind = db.Column(db.String())
    whitelist = db.Column(db.Boolean(), default=True)


class WhitelistWord(db.Model):
    __tablename__ = "whitelistedwords"
    word = db.Column(db.String(), primary_key=True)


class ApprovedInvite(db.Model):
    __tablename__ = "approvedinvites"
    code = db.Column(db.String(), primary_key=True)
    uses = db.Column(db.Integer(), default=-1)
    alias = db.Column(db.String())

    @property
    def is_temporary(self):
        return self.uses > 0


class Rule(db.Model):
    __tablename__ = "rules"
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String())


class RemindMeEntry(db.Model):
    __tablename__ = "remindmeentries"
    id = db.Column(db.BigInteger(), primary_key=True)
    date = db.Column(db.TIMESTAMP, nullable=False)
    author = db.Column(db.BigInteger, db.ForeignKey("members.id"), nullable=False)
    reminder = db.Column(db.String, nullable=False)


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.BigInteger(), primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    content = db.Column(db.String, nullable=False)
    author = db.Column(db.BigInteger, db.ForeignKey("members.id"), nullable=False)


class Citizen(db.Model):
    __tablename__ = "citizens"
    id = db.Column(db.BigInteger, db.ForeignKey("members.id"), primary_key=True)
    social_credit = db.Column(db.Integer, nullable=False)


class VoteView(db.Model):
    __tablename__ = "voteviews"
    id = db.Column(db.BigInteger(), primary_key=True)
    message_id = db.Column(db.BigInteger())
    identifier = db.Column(db.String, nullable=False)
    author_id = db.Column(db.BigInteger())
    options = db.Column(db.String())
    start = db.Column(db.TIMESTAMP)


class VoteViewVote(db.Model):
    __tablename__ = "voteviewvotes"
    view_id = db.Column(db.BigInteger(), db.ForeignKey("voteviews.id", ondelete='CASCADE'), primary_key=True)
    voter_id = db.Column(db.BigInteger(), primary_key=True)
    option = db.Column(db.String, nullable=False)
