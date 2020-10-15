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
    fc_3ds = db.Column(db.BigInteger)


class Channel(db.Model):
    __tablename__ = "channels"
    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.Unicode)
    private = db.Column(db.Boolean(), default=False)
    nofilter = db.Column(db.Boolean(), default=False)


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


class ApprovedInvite(db.Model):
    __tablename__ = "approvedinvites"
    code = db.Column(db.String(), primary_key=True)
    uses = db.Column(db.Integer(), default=-1)
    alias = db.Column(db.String())

    @property
    def is_temporary(self):
        return self.uses > 0
