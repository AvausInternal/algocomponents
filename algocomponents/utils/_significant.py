from algocomponents.utils import LoggieDoggie
from scipy import stats

class Significant(LoggieDoggie):
    """ """
    default_power = 0.8
    default_significance_level = 0.05
    default_tail = "two_sided"

    def is_significant(
        n1 : int,
        n2 : int,
        p1 : float,
        p2 : float,
        sig_level = default_significance_level,
        tail = default_tail, 
        ):
        """Test to see if the Null Hypothesis that `d = 0` can be disregarded for `d = d1 - d2`.
        Using Z-test with the pooled standard error.

        Args:
        ------
            n1 (int): target group size

            n2 (int): control group size

            p1 (float): probability of success for target group.

            p2 (float): probability of success for control group, sometimes
            referred to as `baseline conversion rate`.

            sig_level (float): significance level often denoted as alpha, typically 0.05.

            tail (string): `one_sided` or `two_sided` test.
        """

        M1 = n1 * p1     # Convert to absolute numbers
        M2 = n2 * p2     # Convert to absolute numbers

        if tail == "two_sided":
            tail_prob = 1 - (
                sig_level / 2
            )  # Convert CI to expected format of stats.t.ppf (Assuming two-sided)

        elif tail == "one_sided":
            tail_prob = (
                1 - sig_level
            )  # Convert CI to expected format of stats.t.ppf (Assuming one-sided)

        z_crit = stats.t.ppf(q=tail_prob, df=1e6)           # "degrees of freedom" (df) is set to be "inf". Assuming inf=1e6.
        p_hat = ( M1 + M2 ) / ( n1 + n2 )
        z = ( p1 - p2 ) / ( p_hat * ( 1 - p_hat ) * ( 1 / n1 + 1 / n2 ) )**(0.5)
        
        p_val = 1 - stats.norm.cdf(z)
        if tail == "two_sided": 
            p_val *= 2 # If two-sided ww simply multiply by two
        

        self.logger.info(f"Specified Significance level: {self.significance_level}.")
        self.logger.info(f"Critical test statistic (z-score): {z_crit}.")
        self.logger.info(f"Observed test statistic (z-score)= {abs(z)}.")
        self.logger.info(f"Observed p-value: {p_val}.")

        if abs(z) > z_crit:
            print(f"Significant result! Test statistic = {abs(z)} and p-value = {p_val}.")
        else:
            print(f"NON Significant result! Test statistic = {abs(z)} and p-value = {p_val}.")

        self.observed_test_statistic = z
        self.observed_p_value = p_val