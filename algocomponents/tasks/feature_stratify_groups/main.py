from algocomponents.adapters import GCPAdapter
from pipe_line.Stratify_Groups import Stratify_Groups

sql_pipeline = Stratify_Groups(
    sql_adapter=GCPAdapter(),
    input_table="Customer",
    primary_keys=["CustomerId"],
    stratify_on="CustomerId, Country, City",
    nbr_groups=4,
    output_table="Stratified",
)

sql_pipeline.start()
