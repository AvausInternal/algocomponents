from abc import ABC, abstractmethod

from common.loggiedoggie import LoggieDoggie


class SQLAdapter(LoggieDoggie, ABC):
    """An abstract adapter used for connecting to a service and running queries.

    The purpose of the sql adapter is to generalize how we set up connections to
    different services. There will be one adapter per service.
    """

    def __init__(self, config):
        super().__init__()
        self.config = config

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def check_connection(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def run_sql(self, sql: str):
        pass

    def run_sql_file(self, path: str):
        with open(path) as f:
            sql = f.read()
            queries = sql.split(";")
            for query in queries:
                query = query.strip()
                if query:
                    self.run_sql(query)
