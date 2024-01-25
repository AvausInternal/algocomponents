from typing import List
from algocomponents.tasks import SQLPipeline


class MapStringSegmentsToInt(SQLPipeline):
    """A task for mapping string segments to integers. 
    
    It is useful for situations where model generates
    multiple predictions per unique entity, and we want to
    send those scores to a tool which does not accept strings.
    """

    def __init__(
        self,
        input_table: str,
        mapping_table: str,
        output_table: str,
        identifier_columns: List[str],
        segment_column: str = "segment",
        mapped_segment_column: str = "mapped_segment",
        **kwargs
    ):
        super().__init__(**kwargs)
        self.add_to_config("input_table", input_table)
        self.add_to_config("mapping_table", mapping_table)
        self.add_to_config("output_table", output_table)
        self.add_to_config("identifier_columns", ", ".join(identifier_columns))
        self.add_to_config("segment_column", segment_column)
        self.add_to_config("mapped_segment_column", mapped_segment_column)
