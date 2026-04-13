# pg-db-conn-manager
A simple package that wraps pgsql connection.  

# Copy simplified
Wraps the copy method. Simplifies the usage of the copy method. Autogenerate the query around the creation of the object.

# Use example
```python
from pg_db_manager import DBConnection, CopyDir

with DBConnection(host, password, database, user) as conn:
    with conn.copy(CopyDir.FROM) as cp:
        cp.write(data)
```