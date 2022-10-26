from algocomponents.adapters import GCPAdapter
from pipe_line.StratifyGroups import StratifyGroups

sql_pipeline = StratifyGroups(
    sql_adapter=GCPAdapter(),
    input_table='tmp.Customer',
    primary_keys=["CustomerId"],
    stratify_on=["City", "Country"],
    nbr_groups=3,
    output_table='tmp.Stratified_groups')

sql_pipeline.start()
