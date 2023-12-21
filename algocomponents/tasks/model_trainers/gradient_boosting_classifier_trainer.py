from typing import List

from sklearn.ensemble import GradientBoostingClassifier

from algocomponents.tasks import ModelTrainer


class GradientBoostingClassifierTrainer(ModelTrainer):
    """Trains a model using GradientBoostingClassifier() from scikit-learn.

    Inherits from ModelTrainer which does all the work. This class is just a way
    to call it with the correct arguments to train with this specific model.

    Args:
        dataset_table: Full path to table where data to train model is.
        target_label_column: Name of target label column.
        output_path: Path to folder where model files will be saved.
        categorical_columns: Which columns to one_hot_encode. Can have any data type.
        excluded_columns: Columns to not use when training (for example primary keys)
        overwrite_existing_model: If True, anything at the file destination will be
            deleted before saving the model.

    """

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
            model_type="classification",
            model_reference=GradientBoostingClassifier(),
            **kwargs,
        )
