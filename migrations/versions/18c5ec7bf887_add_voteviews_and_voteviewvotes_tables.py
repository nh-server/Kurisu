"""add voteviews and voteviewvotes tables

Revision ID: 18c5ec7bf887
Revises: 01c719fe3b1f
Create Date: 2022-04-08 13:36:46.958088

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18c5ec7bf887'
down_revision = '01c719fe3b1f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('voteviews',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('message_id', sa.BigInteger(), nullable=True),
    sa.Column('identifier', sa.String(), nullable=False),
    sa.Column('author_id', sa.BigInteger(), nullable=True),
    sa.Column('options', sa.String(), nullable=True),
    sa.Column('start', sa.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('voteviewvotes',
    sa.Column('view_id', sa.BigInteger(), nullable=False),
    sa.Column('voter_id', sa.BigInteger(), nullable=False),
    sa.Column('option', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['view_id'], ['voteviews.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('view_id', 'voter_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('voteviewvotes')
    op.drop_table('voteviews')
    # ### end Alembic commands ###