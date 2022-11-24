from abc import ABC, abstractmethod
from typing import List


class ModelBase(ABC):

    """An abstract base class for ML model prediction code"""

    """
    Properties:
        traget_columns: tagrget column or columns in case of multi-traget 
        feature_columns: training features with out traget labels from the data source

    Args:
        training_table_path: data source for model training.
    """

    @property
    @abstractmethod
    def traget_columns(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def feature_columns(self) -> List[str]:
        pass

    def __init__(
        self,
        training_data_path: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.training_data_path = training_data_path.format(**self.config[self.section])
        self.add_to_config("training_data_path", self.training_data_path)
        self.model_name = type(self).__name__

    @property
    @abstractmethod
    def input_schema(self):

        """
        This abstract property returns the schema that is accepted by the predict() method.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def output_schema(self):

        """
        This abstract property returns the schema that is returned by the predict() method.
        """
        raise NotImplementedError()

    def set_hyperparams(self):
        raise NotImplementedError()

    def get_hyperparams():
        raise NotImplementedError()

    def train(self):

        """
        module bule print:
          -> get training data and convert to dataframe
          -> train and test split
          -> check if model name qualifies the default standard
          -> train model
          -> test model
          -> dump model as pickle file in cloud storage

        """
        pass

    def load_model(self, model_name):

        """
        module bule print:
             -> check if the model_name exists
             -> load model in required env
        """

        pass

    @abstractmethod
    def predict(self, data, model_name):
        """
        module blue print:
                ->use load_model to get the model trained
                -> validate schema
                -> run prediction
                -> convert prediction to a data frame
                -> export prediction to cloud env

        """
        self.input_schema.validate(
            data
        )  # make sure prediction data schema match the schema of training data
