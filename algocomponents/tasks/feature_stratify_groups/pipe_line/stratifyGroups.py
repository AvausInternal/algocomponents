from algocomponents.tasks import SQLPipeline
from algocomponents.adapters import SQLAdapter


class StratifyGroups(SQLPipeline):
    """Given a table, a set of columns that decide the group,
    what columns to stratify on and how many groups,
    an output table is created with stratified groups."""

    def __init__(
        self,
        sql_adapter: SQLAdapter,
        input_table: str,
        stratify_on: str,
        nbr_groups: int,
        output_table: str,
    ):
        super().__init__(sql_adapter=sql_adapter)
        self.add_to_config("INPUT_TABLE", input_table)
        self.add_to_config("STRATIFY_ON", stratify_on)
        self.add_to_config("NBR_GROUPS", nbr_groups)
        self.add_to_config("OUTPUT_TABLE", output_table)
