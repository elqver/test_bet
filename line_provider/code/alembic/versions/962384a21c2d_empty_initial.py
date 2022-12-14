"""empty-initial

Revision ID: 962384a21c2d
Revises: 
Create Date: 2022-08-28 19:47:27.379622

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '962384a21c2d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lp_event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('coefficient', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('deadline', sa.DateTime(), nullable=True),
    sa.Column('state', sa.Enum('NEW', 'FINISHED_WIN', 'FINISHED_LOSE', name='eventstate'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('lp_event')
    # ### end Alembic commands ###
