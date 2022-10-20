from algocomponents.adapters import SparkAdapter


class DatabricksAdapter(SparkAdapter):
    """Used to run queries in databricks notebooks

    Databricks notebooks use spark, but the notebook itself keeps track of a
    spark context and stops it when necessary. Therefore, this adapter works the
    exact same was as the SparkAdapter, except that it does not stop the spark
    context when disconnecting.

    """

    def disconnect(self):
        """Overwritten to do nothing"""
        pass
