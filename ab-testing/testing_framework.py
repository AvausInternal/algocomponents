from metric_creator import MetricCreator
from test_creator import TestCreator
from test_evaluator import TestEvaluator
from tables_creator import TableCreator

class TestingFramework:
    def __init__(self, test_config_path):
        self.table_creator = TableCreator()
        self.test_creator = TestCreator(test_config_path)
        
        self.metric = None
        self.evaluator = None
                
    def create_test(self, mode='add'):
        self.test_creator.create_test(mode)
            
    def delete_test(self):
        self.test_creator.delete_test()
        
    def create_metric(
                self,
                metric_name,
                description,
                sql,
                mode='add'
                    ):
        self.metric = MetricCreator(
                            metric_name=metric_name,
                            description=description,
                            sql=sql)
        self.metric.create_metric(mode)
        
    def delete_metric(self, mode='add'):
        self.delete_metric(self, mode)
            
    def evaluate_test(self, test_name, mode='add'):
        self.evaluator = TestEvaluator(test_name)
        self.evaluator.evaluate_test(mode)