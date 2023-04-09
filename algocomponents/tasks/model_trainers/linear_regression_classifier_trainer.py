from typing import List

from sklearn.linear_model import LinearRegression

from algocomponents.tasks import ModelTrainer


class LinearRegressionClassifierTrainer(ModelTrainer):
    def __init__(
        self,
        dataset_table: str,
        target_label_column: str,
        output_path: str,
        one_hot_encoded_columns: List[str] = None,
        excluded_columns: List[str] = None,
        overwrite_existing_model: bool = False,
        **kwargs
    ):
        super().__init__(
            dataset_table=dataset_table,
            target_label_column=target_label_column,
            output_path=output_path,
            one_hot_encoded_columns=one_hot_encoded_columns,
            excluded_columns=excluded_columns,
            overwrite_existing_model=overwrite_existing_model,
            model_type="classifier",
            model_reference=LinearRegression(),
            **kwargs,
        )
