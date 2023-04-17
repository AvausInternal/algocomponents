from typing import List

from sklearn.ensemble import RandomForestClassifier

from algocomponents.tasks import ModelTrainer


class RandomForestClassifierTrainer(ModelTrainer):
    def __init__(
        self,
        dataset_table: str,
        target_label_column: str,
        output_path: str,
        categorical_columns: List[str] = None,
        excluded_columns: List[str] = None,
        overwrite_existing_model: bool = False,
        **kwargs
    ):
        super().__init__(
            dataset_table=dataset_table,
            target_label_column=target_label_column,
            output_path=output_path,
            categorical_columns=categorical_columns,
            excluded_columns=excluded_columns,
            overwrite_existing_model=overwrite_existing_model,
            model_type="classifier",
            model_reference=RandomForestClassifier(),
            **kwargs,
        )
