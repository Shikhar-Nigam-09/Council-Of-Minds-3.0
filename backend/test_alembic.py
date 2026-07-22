from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa

context = MigrationContext.configure(dialect=postgresql.dialect())
op = Operations(context)

enum_sa = sa.Enum('a', 'b', name='myenum', create_type=False)
enum_pg = postgresql.ENUM('a', 'b', name='myenum_pg', create_type=False)

def emit_create_table(col_type, table_name):
    op.create_table(table_name, sa.Column('status', col_type))

# Let's intercept the operations
from alembic.operations.ops import CreateTableOp
from alembic.ddl.postgresql import PostgresqlImpl

# Wait, the easiest way is to mock an offline context
def write_ddl(text, *args, **kwargs):
    print(text)

context = MigrationContext.configure(
    dialect=postgresql.dialect(),
    opts={"as_sql": True},
)
op = Operations(context)

with context.begin_transaction():
    op.create_table('table_sa', sa.Column('status', sa.Enum('a', 'b', name='enum_sa', create_type=False)))
    op.create_table('table_pg', sa.Column('status', postgresql.ENUM('a', 'b', name='enum_pg', create_type=False)))
