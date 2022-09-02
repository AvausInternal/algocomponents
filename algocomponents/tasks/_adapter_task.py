from algocomponents.adapters import SQLAdapter
from algocomponents.tasks import Task


class AdapterTask(Task):
    """A task that has access to an adapter

    An adapter can be used to run queries to whichever source the adapter uses.
    The adapter task will disconnect it's adapter if it is not inherited from
    it's parent. This happens either if this is the only task, or if this is
    called from a GroupTask that has another adapter set.
    """

    def __init__(
        self,
        sql_adapter: SQLAdapter = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if sql_adapter:
            self.sql_adapter = sql_adapter
        if not hasattr(self, "sql_adapter"):
            self.sql_adapter = None

    def shutdown(self):
        if self.sql_adapter is not None and self.sql_adapter.is_connected():
            if not self.parent:
                self.sql_adapter.disconnect()
            elif not hasattr(self.parent, "sql_adapter"):
                self.sql_adapter.disconnect()
            elif self.sql_adapter != self.parent.sql_adapter:
                self.sql_adapter.disconnect()
        super().shutdown()

    def set_sql_adapter(self, sql_adapter):
        self.sql_adapter = sql_adapter
