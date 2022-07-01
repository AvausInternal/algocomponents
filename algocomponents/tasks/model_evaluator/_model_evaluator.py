from configparser import ConfigParser

from algocomponents.tasks import SQLPipeline
from algocomponents.adapters import SQLAdapter


class ModelEvaluator(SQLPipeline):
    """A task to evaluate models.

    The task takes an input table with a prediction column
    and a target label column. The task calculates different
    evaluation metrics such as: true positives, false positives,
    true negatives, false negatives, accuracy, precision, recall,
    f1 score for different threshold boundaries.
    """

    def __init__(
        self,
        input_table: str,
        output_table: str,
        prediction_column: str,
        target_label_column: str,
        sql_adapter: SQLAdapter = None,
        config: ConfigParser = None,
        section: str = None,
    ):
        super().__init__(sql_adapter=sql_adapter, config=config, section=section)

        self.add_to_config("INPUT_TABLE", input_table)
        self.add_to_config("OUTPUT_TABLE", output_table)
        self.add_to_config("PREDICTION_COLUMN", prediction_column)
        self.add_to_config("TARGET_LABEL_COLUMN", target_label_column)
        self.add_to_config("THRESHOLD_STRING", self.create_thresholds(100))

    def create_thresholds(self, n_thresholds):
        step = 100 / n_thresholds
        s = f"SELECT {step/100} AS threshold"
        for i in range(2 * int(step), 100, int(step)):
            s += f" UNION ALL SELECT {i/100} AS threshold"
        return s
