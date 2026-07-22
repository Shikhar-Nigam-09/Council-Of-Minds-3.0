import sqlalchemy as sa
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql

enum_sa = sa.Enum('a', 'b', name='myenum', create_type=False)
col_sa = sa.Column('status', enum_sa)
tbl_sa = sa.Table('mytable1', sa.MetaData(), col_sa)

enum_pg = postgresql.ENUM('a', 'b', name='myenum', create_type=False)
col_pg = sa.Column('status', enum_pg)
tbl_pg = sa.Table('mytable2', sa.MetaData(), col_pg)

print("SA Enum:")
print(str(CreateTable(tbl_sa).compile(dialect=postgresql.dialect())))

print("PG Enum:")
print(str(CreateTable(tbl_pg).compile(dialect=postgresql.dialect())))
