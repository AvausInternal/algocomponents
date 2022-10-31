from algocomponents.adapters import SQLAdapter
from algocomponents.tasks import Task


class AdapterTask(Task):
    """A task that has access to an adapter.

    An adapter can be used to run queries to whichever source the adapter uses.
    The adapter task will disconnect it's adapter if it is not inherited from
    it's parent. This happens either if this is the only task, or if this is
    called from a GroupTask that has another adapter set.

    Args:
        sql_adapter: The adapter the task will use.

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
        """Disconnects the sql_adapter, if no other task will use it.

        We will try to disconnect if we have an adapter and it is connected.

        We disconnect if either of these are true:
            - There is no parent.
            - The parent does not have an sql_adapter.
            - The parent does not have the same sql_adapter.

        In other words: Disconnect unless we share the adapter with our parent.

        The most common scenario is that one sql_adapter is used throughout a
        GroupTask: It passes it's sql_adapter to all it's children. Since that
        GroupTasks shutdown() is the last method to run, and it is the only task
        that does not have a parent, the last thing that happens is that the
        sql_adapter is disconnected.

        However, more complicated setups are supported, where as parts of a
        task-tree have their own adapters.

        """
        if self.sql_adapter is not None and self.sql_adapter.is_connected():
            if not self.parent:
                self.sql_adapter.disconnect()
            elif not hasattr(self.parent, "sql_adapter"):
                self.sql_adapter.disconnect()
            elif self.sql_adapter != self.parent.sql_adapter:
                self.sql_adapter.disconnect()
        super().shutdown()

    def set_sql_adapter(self, sql_adapter):
        """Set the SQLAdapter for this AdapterTask

        This is implemented as a method in order for GroupTasks to recursively
        set_sql_adapter in a task-tree.

        Args:
            sql_adapter: The SQLAdapter to set

        """
        self.sql_adapter = sql_adapter
