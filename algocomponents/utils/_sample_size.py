from algocomponents.utils import LoggieDoggie
from scipy import stats


class SampleSize(LoggieDoggie):
    """Sample size calculations."""

    default_power = 0.8
    default_significance_level = 0.05
    default_tail = "two_sided"

    def get_min_sample_size_binomial(
        self,
        p1: float,
        p2: float,
        power=default_power,
        sig_level=default_significance_level,
        tail=default_tail,
    ):

        """Returns the minimum sample size to set up an A/B test for a binomial metric.

        We assume the same sample size for both test and control group.

        Args:
        -------
            p1 (float): probability of success for target group.

            p2 (float): probability of success for control group, sometimes
            referred to as `baseline conversion rate`.

            power (float): probability of rejecting the null hypothesis when the null hypothesis is false, typically 0.8.

            sig_level (float): significance level often denoted as alpha, typically 0.05.

            tail (string): `one_sided` or `two_sided` test.

        Returns:
        -------
            min_N (float): minimum sample size required in each group.

        References:
        -------
            Placeholder Link to confluence

        """

        if tail == "two_sided":
            tail_prob = 1 - (
                sig_level / 2
            )  # Convert CI to expected format of stats.t.ppf (Assuming two-sided)

        elif tail == "one_sided":
            tail_prob = (
                1 - sig_level
            )  # Convert CI to expected format of stats.t.ppf (Assuming one-sided)

        # Standard normal distribution to determine z-values
        standard_norm = stats.norm(0, 1)

        # Find Z_beta from desired power
        Z_beta = standard_norm.ppf(power)

        # Find Z_alpha
        Z_alpha = standard_norm.ppf(tail_prob)

        # Find smallest sample size required in each group.
        min_n = ((p1 * (1 - p1) + p2 * (1 - p2)) * (Z_beta + Z_alpha) ** 2) / (
            p1 - p2
        ) ** 2

        self.logger.info("Minimum sample size of each group is: ", round(min_n))
        return round(min_n)
    
    def get_min_sample_size_continuous(
        self,
        u1: float,
        u2: float,
        var: float,
        power=default_power,
        sig_level=default_significance_level,
        tail=default_tail,
    ):

        """Returns the minimum sample size to set up an A/B test for a continuous metric.

        We assume the same sample size for both test and control group.

        Args:
        -------
            u1 (float): expected value for target group.

            u2 (float): estimated value for control group.

            var (float): estimated variance for control group.

            power (float): probability of rejecting the null hypothesis when the null hypothesis is false, typically 0.8.

            sig_level (float): significance level often denoted as alpha, typically 0.05.

            tail (string): `one_sided` or `two_sided` test.

        Returns:
        -------
            min_N (float): minimum sample size required in each group.

        References:
        -------
            Placeholder Link to confluence

        """

        if tail == "two_sided":
            tail_prob = 1 - (
                sig_level / 2
            )  # Convert CI to expected format of stats.t.ppf (Assuming two-sided)

        elif tail == "one_sided":
            tail_prob = (
                1 - sig_level
            )  # Convert CI to expected format of stats.t.ppf (Assuming one-sided)

        # Standard normal distribution to determine z-values
        standard_norm = stats.norm(0, 1)

        # Find Z_beta from desired power
        Z_beta = standard_norm.ppf(power)

        # Find Z_alpha
        Z_alpha = standard_norm.ppf(tail_prob)

        # Find smallest sample size required in each group.
        min_n = (2 * (var) * (Z_beta + Z_alpha) ** 2) / (u1 - u2) ** 2
        self.logger.info("Minimum sample size of each group is: ", round(min_n))
        return round(min_n)

    def get_unequal_sample_size(self, N: int, N_adj: int):
        """Returns the minimum sample size of the control group
        when the samples have unequal size.

        When the control and target groups are of different sizes, the total sample size
        needs to be adjusted because unequal groups produces higher variance in the test statistic.


        Args:
        -------
            N (int): The minimal sample size (both test & control group).
            N_adj (int): The adjusted sample size. Needs to be bigger than N.

        Returns:
        -------
            control_sample_size (int):
            test_sample_size (int):

        References:
        -------

        """

        k = SampleSize.get_control_group_ratio_constant(N, N_adj)
        prop_control = 1 / (1 + k)
        control_sample_size = round(prop_control * N_adj)
        test_sample_size = round(N_adj - N_adj * prop_control)

        self.logger.info("Control group proportion: ", prop_control)
        self.logger.info("Control group size: ", control_sample_size)
        self.logger.info("Test group size: ", test_sample_size)

        return (control_sample_size, test_sample_size)

    def get_control_group_ratio_constant(N: int, N_adj: int):
        """Returns the control group ratio constant k."""

        k = -(2 * N - 4 * N_adj) / (2 * N) + (
            ((2 * N - 4 * N_adj) / (2 * N)) ** 2 - 1
        ) ** (1 / 2)
        return k
