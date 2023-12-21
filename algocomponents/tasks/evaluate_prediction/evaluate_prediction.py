from algocomponents.tasks import SQLPipeline


class EvaluatePrediction(SQLPipeline):
    """A task to evaluate a prediction done by a model.

    The task takes an input table with a prediction column and a target label
    column. The task calculates different evaluation metrics such as: true
    positives, false positives, true negatives, false negatives, accuracy,
    precision, recall, f1 score for different threshold boundaries.

    Args:
        input_table: Table where model predictions and target labels exists.
        output_table: Table where results should be put.
        prediction_column: Column in input table for model predictions.
        target_label_column: Column in input table for model target label.

    """

    def __init__(
        self,
        input_table: str,
        output_table: str,
        prediction_column: str,
        target_label_column: str,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.add_to_config("input_table", input_table)
        self.add_to_config("output_table", output_table)
        self.add_to_config("prediction_column", prediction_column)
        self.add_to_config("target_label_column", target_label_column)
        self.add_to_config("threshold_string", self.create_thresholds(100))

    def create_thresholds(self, n_thresholds) -> str:
        """Creates a query that produces a table with n_thresholds.

        Args:
            n_thresholds: How many thresholds, or how many rows, to produce.

        Returns:
            The query for creating n thresholds.

        """
        step = 100 / n_thresholds
        s = f"SELECT {step/100} AS threshold"
        for i in range(2 * int(step), 100, int(step)):
            s += f" UNION ALL SELECT {i/100} AS threshold"
        return s
