from typing import List

from algocomponents.tasks import SQLPipeline
from algocomponents.tasks.stratify_groups.stratify_groups import StratifyGroups


class DownsampleTable(SQLPipeline):
    """Performs a stratified downsampling of a table.

    This task uses StratifyGroups to stratify into a required number of groups,
    and then selects group 1 of that table as the output table.

    Args:
        input_table: The name for the table to downsample
        output_table: Where to save the downsampled table
        downsample_ratio: What percentage of the original table to keep
        stratify_on: Which columns in the original table to stratify on in order
                     to keep the original table distribution.

    """

    def __init__(
        self,
        input_table: str,
        output_table: str,
        downsample_ratio: float,
        stratify_on: List[str],
        **kwargs,
    ):
        super().__init__(**kwargs)

        if downsample_ratio >= 1.0:
            raise ValueError(
                f"Downsample ratio must be 1 or smaller, got {downsample_ratio}"
            )

        self.input_table = input_table
        self.stratify_in_between_table = f"{output_table}_prep"
        self.output_table = output_table
        self.downsample_ratio = downsample_ratio
        self.stratify_on = stratify_on

        self.add_to_config("input_table", input_table)
        self.add_to_config("stratify_in_between_table", self.stratify_in_between_table)
        self.add_to_config("output_table", output_table)
        self.add_to_config("downsample_ratio", downsample_ratio)

    def run(self):
        StratifyGroups(
            sql_adapter=self.sql_adapter,
            input_table=self.input_table,
            output_table=self.stratify_in_between_table,
            stratify_on=self.stratify_on,
            n_groups=int(1 / self.downsample_ratio),
        ).start()
        super().run()
