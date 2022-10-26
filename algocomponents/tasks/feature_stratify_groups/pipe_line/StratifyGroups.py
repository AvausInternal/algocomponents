from algocomponents.tasks import SQLPipeline
from algocomponents.adapters import SQLAdapter


class StratifyGroups(SQLPipeline):
    """ Given a table, a set of columns that decide the group, 
    what columns to stratify on and how many groups, 
    an output table is created with stratified groups. """

    def __init__(
            self,
            sql_adapter: SQLAdapter,
            input_table: str,  # CUSTOMER_DB.all_profilable_customers
            primary_keys: list,  # ["customer_key"]
            stratify_on: list,  # ["age", "postal_code"]
            nbr_groups: int,  # 2
            output_table: str,  # AB_TESTING_DB.my_test_groups
    ):
        super().__init__(sql_adapter=sql_adapter)
        self.add_to_config("Input_table", input_table)
        self.add_to_config("Primary_keys", primary_keys)
        self.add_to_config("Stratify_on", stratify_on)
        self.add_to_config("Nbr_groups", nbr_groups)
        self.add_to_config("Output_table", output_table)
