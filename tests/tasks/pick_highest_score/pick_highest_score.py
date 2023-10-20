from typing import List
from algocomponents.tasks import SQLPipeline


class PickHighestScore(SQLPipeline):
    """A task for picking the highest score out of a scores table.
    
    This is applicable for models which produce more than 1 score per desired unique entity (e.g. customers or subscriptions).
    """
    def __init__(
        self,
        input_table: str,
        output_table: str,
        identifier_columns: List[str],
        model_name: str,
        segment_column: str = "segment",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.add_to_config("input_table", input_table)
        self.add_to_config("output_table", output_table)
        self.add_to_config("identifier_columns", ", ".join(identifier_columns))
        self.add_to_config("model_name", model_name)
        self.add_to_config("segment_column", segment_column)
