"""v0.0.5

Revision ID: e33645bcd5a9
Revises: beb959117a4a
Create Date: 2024-04-05 12:59:05.124079

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e33645bcd5a9'
down_revision: Union[str, None] = 'beb959117a4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('friend_request', sa.Column('sender_id', sa.BigInteger(), nullable=False))
    op.add_column('friend_request', sa.Column('receiver_id', sa.BigInteger(), nullable=False))
    op.drop_constraint('friend_request_receiver_name_fkey', 'friend_request', type_='foreignkey')
    op.drop_constraint('friend_request_sender_name_fkey', 'friend_request', type_='foreignkey')
    op.create_foreign_key(None, 'friend_request', 'user', ['receiver_id'], ['id'])
    op.create_foreign_key(None, 'friend_request', 'user', ['sender_id'], ['id'])
    op.drop_column('friend_request', 'receiver_name')
    op.drop_column('friend_request', 'sender_name')
    op.add_column('friendship', sa.Column('user_id', sa.BigInteger(), nullable=False))
    op.add_column('friendship', sa.Column('friend_id', sa.BigInteger(), nullable=False))
    op.drop_constraint('friendship_friend_name_fkey', 'friendship', type_='foreignkey')
    op.drop_constraint('friendship_user_name_fkey', 'friendship', type_='foreignkey')
    op.create_foreign_key(None, 'friendship', 'user', ['user_id'], ['id'])
    op.create_foreign_key(None, 'friendship', 'user', ['friend_id'], ['id'])
    op.drop_column('friendship', 'user_name')
    op.drop_column('friendship', 'friend_name')
    op.add_column('notification', sa.Column('user_id', sa.BigInteger(), nullable=False))
    op.drop_constraint('notification_username_fkey', 'notification', type_='foreignkey')
    op.create_foreign_key(None, 'notification', 'user', ['user_id'], ['id'])
    op.drop_column('notification', 'username')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notification', sa.Column('username', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'notification', type_='foreignkey')
    op.create_foreign_key('notification_username_fkey', 'notification', 'user', ['username'], ['username'])
    op.drop_column('notification', 'user_id')
    op.add_column('friendship', sa.Column('friend_name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('friendship', sa.Column('user_name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'friendship', type_='foreignkey')
    op.drop_constraint(None, 'friendship', type_='foreignkey')
    op.create_foreign_key('friendship_user_name_fkey', 'friendship', 'user', ['user_name'], ['username'])
    op.create_foreign_key('friendship_friend_name_fkey', 'friendship', 'user', ['friend_name'], ['username'])
    op.drop_column('friendship', 'friend_id')
    op.drop_column('friendship', 'user_id')
    op.add_column('friend_request', sa.Column('sender_name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('friend_request', sa.Column('receiver_name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'friend_request', type_='foreignkey')
    op.drop_constraint(None, 'friend_request', type_='foreignkey')
    op.create_foreign_key('friend_request_sender_name_fkey', 'friend_request', 'user', ['sender_name'], ['username'])
    op.create_foreign_key('friend_request_receiver_name_fkey', 'friend_request', 'user', ['receiver_name'], ['username'])
    op.drop_column('friend_request', 'receiver_id')
    op.drop_column('friend_request', 'sender_id')
    # ### end Alembic commands ###