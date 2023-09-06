"""additional_fields_for__charge_points_table

Revision ID: 0003
Revises: 0002
Create Date: 2023-07-11 18:27:06.983950

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('charge_points', sa.Column('manufacturer', sa.String(), nullable=False))
    op.add_column('charge_points', sa.Column('latitude', sa.Numeric(), nullable=True))
    op.add_column('charge_points', sa.Column('longitude', sa.Numeric(), nullable=True))
    op.add_column('charge_points', sa.Column('serial_number', sa.String(), nullable=False, unique=True))
    op.add_column('charge_points', sa.Column('comment', sa.String(), nullable=True))
    op.add_column('charge_points', sa.Column('model', sa.String(), nullable=False))
    op.add_column('charge_points', sa.Column('password', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('charge_points', 'model')
    op.drop_column('charge_points', 'comment')
    op.drop_column('charge_points', 'unavailability_reason')
    op.drop_column('charge_points', 'serial_number')
    op.drop_column('charge_points', 'longitude')
    op.drop_column('charge_points', 'latitude')
    op.drop_column('charge_points', 'manufacturer')
    # ### end Alembic commands ###