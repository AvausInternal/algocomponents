import math

from scipy import stats

from algocomponents.utils import LoggieDoggie


class ABTools(LoggieDoggie):
    """A/B testing tools

    ABTools contain a number of methods that are useful for conducting A/B tests
    and report results of A/B tests.

    Methods
    -------
    get_min_sample_size_binomial():
        Calculate the minimum sample size to set up an A/B test for a binomial metric.
    get_min_sample_size_continuous():
        Calculate the minimum sample size to set up an A/B test for a continuous metric.
    get_unequal_sample_size():
        Calculate the minimum sample size of the control group when the samples have unequal size.
    is_significant_binomial():
        Calculate if an A/B test with binomial metric was statistically significant (Z-test).
    is_significant_continuous()
        Calculate if an A/B test with continuous metric was statistically significant (Welch's t-test).
    """

    _default_power = 0.8
    _default_significance_level = 0.05
    _default_tail = "two_sided"

    def __init__(self):
        self.logger = LoggieDoggie().fetch_logger(logger_name="ab_testing_tools")

    def get_min_sample_size_binomial(
        self,
        p1: float,
        p2: float,
        power: float = _default_power,
        sig_level: float = _default_significance_level,
        tail: str = _default_tail,
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
            min_N (int): minimum sample size required in each group.

        """

        if not 0 < power <= 1:
            raise Exception(f"Power must be a float between 0 and 1, got: {power}")
        if not 0 <= sig_level:
            raise Exception(
                f"Sig_level must be a float between 0 and 1, got: {sig_level}"
            )

        if tail == "two_sided":
            tail_prob = 1 - (
                sig_level / 2
            )  # Convert CI to expected format of stats.t.ppf (Assuming two-sided)

        elif tail == "one_sided":
            tail_prob = (
                1 - sig_level
            )  # Convert CI to expected format of stats.t.ppf (Assuming one-sided)
        else:
            raise Exception(f"tail must be either two_sided or one_sided, got: {tail}")

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
        min_n = math.ceil(min_n)
        self.logger.info(f"Minimum sample size of each group is: {min_n}")
        return min_n

    def get_min_sample_size_continuous(
        self,
        u1: float,
        u2: float,
        var: float,
        power: float = _default_power,
        sig_level: float = _default_significance_level,
        tail: str = _default_tail,
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
            min_N (int): minimum sample size required in each group.

        """

        if not 0 < power <= 1:
            raise Exception(f"Power must be a float between 0 and 1, got: {power}")
        if not 0 <= sig_level:
            raise Exception(
                f"Sig_level must be a float between 0 and 1, got: {sig_level}"
            )

        if tail == "two_sided":
            tail_prob = 1 - (
                sig_level / 2
            )  # Convert CI to expected format of stats.t.ppf (Assuming two-sided)

        elif tail == "one_sided":
            tail_prob = (
                1 - sig_level
            )  # Convert CI to expected format of stats.t.ppf (Assuming one-sided)
        else:
            raise Exception(f"tail must be either two_sided or one_sided, got: {tail}")

        # Standard normal distribution to determine z-values
        standard_norm = stats.norm(0, 1)

        # Find Z_beta from desired power
        Z_beta = standard_norm.ppf(power)

        # Find Z_alpha
        Z_alpha = standard_norm.ppf(tail_prob)

        # Find smallest sample size required in each group.
        min_n = (2 * (var) * (Z_beta + Z_alpha) ** 2) / (u1 - u2) ** 2
        min_n = math.ceil(min_n)
        self.logger.info(f"Minimum sample size of each group is: {min_n}")
        return min_n

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

        """

        if N >= N_adj:
            raise ValueError("N_adj needs to be greater than N")

        k = self.get_control_group_ratio_constant(N, N_adj)
        prop_control = 1 / (1 + k)
        control_sample_size = math.ceil(prop_control * N_adj)
        test_sample_size = math.ceil(N_adj - N_adj * prop_control)

        self.logger.info(f"Control group proportion: {prop_control}")
        self.logger.info(f"Control group size: {control_sample_size}")
        self.logger.info(f"Test group size: {test_sample_size}")

        return (control_sample_size, test_sample_size)

    def get_control_group_ratio_constant(self, N: int, N_adj: int):
        """Returns the control group ratio constant k."""

        k = -(2 * N - 4 * N_adj) / (2 * N) + (
            ((2 * N - 4 * N_adj) / (2 * N)) ** 2 - 1
        ) ** (1 / 2)
        return k

    def is_significant_binomial(
        self,
        n1: int,
        n2: int,
        p1: float,
        p2: float,
        sig_level: float = _default_significance_level,
        tail: str = _default_tail,
    ):
        """We test the null hypothesis against the given alternative:

        H0: p1=p2 vs HA: p1!=p2

        using Z-test with the pooled standard error.

        Args:
        ------
            n1 (int): target group size.

            n2 (int): control group size.

            p1 (float): probability of success for target group.

            p2 (float): probability of success for control group, sometimes
            referred to as `baseline conversion rate`.

            sig_level (float): significance level often denoted as alpha, typically 0.05.

            tail (string): `one_sided` or `two_sided` test.

        Returns:
        -------
        z (float): z-score value.
        p (float): p-value.

        """

        if not 0 <= sig_level:
            raise Exception(
                f"Sig_level must be a float between 0 and 1, got: {sig_level}"
            )

        M1 = n1 * p1  # Convert to absolute numbers
        M2 = n2 * p2  # Convert to absolute numbers

        if tail == "two_sided":
            tail_prob = 1 - (
                sig_level / 2
            )  # Convert CI to expected format of stats.t.ppf (Assuming two-sided)

        elif tail == "one_sided":
            tail_prob = (
                1 - sig_level
            )  # Convert CI to expected format of stats.t.ppf (Assuming one-sided)
        else:
            raise Exception(f"tail must be either two_sided or one_sided, got: {tail}")

        z_crit = stats.t.ppf(
            q=tail_prob, df=1e6
        )  # "degrees of freedom" (df) is set to be "inf". Assuming inf=1e6.
        p_hat = (M1 + M2) / (n1 + n2)
        z = (p1 - p2) / (p_hat * (1 - p_hat) * (1 / n1 + 1 / n2)) ** (0.5)

        p_val = 1 - stats.norm.cdf(z)
        if tail == "two_sided":
            p_val *= 2  # If two-sided simply multiply by two

        self.logger.info(f"Specified Significance level: {sig_level}.")
        self.logger.info(f"Critical test statistic (z-score): {z_crit}.")
        self.logger.info(f"Observed test statistic (z-score): {abs(z)}.")
        self.logger.info(f"Observed p-value: {p_val}.")

        if abs(z) > z_crit:
            self.logger.info(
                f"Significant result! Test statistic = {abs(z)} and p-value = {p_val}."
            )
        else:
            self.logger.info(
                f"NON Significant result! Test statistic = {abs(z)} and p-value = {p_val}."
            )

        return (z, p_val)

    def is_significant_continuous(
        self,
        n1,
        n2,
        x1,
        x2,
        var1,
        var2,
        sig_level=_default_significance_level,
        tail=_default_tail,
    ):
        """Welch's t-test. Unequal variance. Unequal or equal sample size.

        We test the null hypothesis against the given alternative:

        H0: p1=p2 vs HA: p1!=p2

        using Welch-test with the unpooled standard error.

        Args:
        ------
            n1 (int): target group size.

            n2 (int): control group size.

            x1 (float): observed value for target group.

            x2 (float): observed value for control group.

            var1 (float): variance of target group.

            var2 (float): variance of control group.

            sig_level (float): significance level often denoted as alpha, typically 0.05.

            tail (string): `one_sided` or `two_sided` test.

        Returns:
        -------
        t (float): t-score value.
        p (float): p-value.

        """

        if not 0 <= sig_level:
            raise Exception(
                f"Sig_level must be a float between 0 and 1, got: {sig_level}"
            )

        s_delta = ((var1 / n1) + (var2 / n2)) ** (0.5)
        t = (x1 - x2) / s_delta
        p_val = 1 - stats.norm.cdf(t)
        if tail == "two_sided":
            p_val *= 2  # If two-sided simply multiply by two

        # Welch Satterthwaite equation for degrees of freedom
        df = (var1 / n1 + var2 / n2) ** 2 / (
            (var1 / n1) ** 2 / (n1 - 1) + (var2 / n2) ** 2 / (n2 - 1)
        )

        if tail == "two_sided":
            tail_prob = 1 - (
                sig_level / 2
            )  # Convert CI to expected format of stats.t.ppf (Assuming two-sided)

        elif tail == "one_sided":
            tail_prob = (
                1 - sig_level
            )  # Convert CI to expected format of stats.t.ppf (Assuming one-sided)
        else:
            raise Exception(f"tail must be either two_sided or one_sided, got: {tail}")

        t_crit = stats.t.ppf(q=tail_prob, df=df)

        self.logger.info(f"Specified Significance level: {sig_level}.")
        self.logger.info(f"Degrees of freedom: {df}")
        self.logger.info(f"Critical test statistic (t-score): {t_crit}.")
        self.logger.info(f"Observed test statistic (t-score): {abs(t)}.")
        self.logger.info(f"Observed p-value: {p_val}.")

        if abs(t) > t_crit:
            self.logger.info(
                f"Significant result! Test statistic = {abs(t)} and p-value = {p_val}."
            )
        else:
            self.logger.info(
                f"NON Significant result! Test statistic = {abs(t)} and p-value = {p_val}."
            )
        return (t, p_val)
