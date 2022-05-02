from algocomponents.adapters._sql_adapter import SQLAdapter
from algocomponents.adapters._local_sqlite_adapter import LocalSqliteAdapter
from algocomponents.adapters._gcp_adapter import GCPAdapter

"""Allows classes to live in separate files while keeping imports short

All the classes are imported into this init-file, and from this file they can
then be imported from the __all__-list, which defines which modules are
available in this package. Note that the modules in the __all__-list must be in
order of dependency: As GCPAdapter inherits from SQLAdapter, SQLAdapter must
precede it.
"""

__all__ = [
    "SQLAdapter",
    "LocalSqliteAdapter",
    "GCPAdapter",
]
