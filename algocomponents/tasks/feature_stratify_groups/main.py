from algocomponents.adapters import GCPAdapter
from pipe_line.stratifyGroups import StratifyGroups

sql_pipeline = StratifyGroups(
    sql_adapter=GCPAdapter(),
    input_table="Customer",
    stratify_on="CustomerId, Country, City",
    nbr_groups=3,
    output_table="Stratified",
)

sql_pipeline.start()
