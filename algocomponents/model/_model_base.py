from abc import ABC, abstractmethod
from typing import List


class ModelBase(ABC):

    """ An abstract base class for ML model prediction code """
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
        pass

  
    def load_model(self):
         pass
        
    
    @abstractmethod
    def predict(self, data):
        self.input_schema.validate(data)   #make sure prediction data schema match the schema of training data

   

  
    




