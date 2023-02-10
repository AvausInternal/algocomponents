from unittest import TestCase

import numpy
from scipy import stats

from algocomponents.utils._ab_tools import ABTools


class TestAbTestMethods(TestCase):
    p1 = 0.05
    p2 = 0.01
    power = 0.8
    sig_level = 0.05
    u1 = 350
    u2 = 300
    var = 50
    tail = "two_sided"
    n1 = 500
    n2 = 500

    def test_sample_size_binomial_output_type(self):
        ab_tools = ABTools()
        min_n = ab_tools.get_min_sample_size_binomial(
            p1=self.p1,
            p2=self.p2,
            power=self.power,
            sig_level=self.sig_level,
            tail=self.tail,
        )
        assert type(min_n) is int

    def test_sample_size_continuous_output_type(self):
        ab_tools = ABTools()
        min_n = ab_tools.get_min_sample_size_continuous(
            u1=self.u1,
            u2=self.u2,
            var=self.var,
            power=self.power,
            sig_level=self.sig_level,
            tail=self.tail,
        )
        assert type(min_n) is int

    def test_is_significant_output_type(self):
        ab_tools = ABTools()
        z, p = ab_tools.is_significant_binomial(
            n1=self.n1,
            n2=self.n2,
            p1=self.p1,
            p2=self.p2,
            sig_level=self.sig_level,
            tail=self.tail,
        )
        assert type(z) is float
        assert type(p) is numpy.float64

    def test_continuous_significant_output_type(self):
        ab_tools = ABTools()
        t, p = ab_tools.is_significant_continuous(
            n1=self.n1,
            n2=self.n2,
            x1=self.u1,
            x2=self.u2,
            var1=self.var,
            var2=self.var,
            sig_level=self.sig_level,
            tail=self.tail,
        )
        assert type(t) is float
        assert type(p) is numpy.float64

    def test_non_significant_binomial_ab_test(self):
        z_crit = stats.t.ppf(q=0.975, df=1e6)
        ab_tools = ABTools()
        t, p = ab_tools.is_significant_binomial(
            n1=1000, n2=1000, p1=0.01, p2=0.01, tail="two_sided"
        )
        assert z_crit > abs(t)

    def test_significant_binomial_ab_test(self):
        z_crit = stats.t.ppf(q=0.975, df=1e6)
        ab_tools = ABTools()
        t, p = ab_tools.is_significant_binomial(
            n1=1000, n2=1000, p1=0.03, p2=0.01, tail="two_sided"
        )
        assert z_crit < abs(t)

    def test_non_significant_continuous_ab_test(self):
        ab_tools = ABTools()
        n1 = 9
        n2 = 8
        var1 = 56**2
        var2 = 112**2
        df = (var1 / n1 + var2 / n2) ** 2 / (
            (var1 / n1) ** 2 / (n1 - 1) + (var2 / n2) ** 2 / (n2 - 1)
        )
        t_crit = stats.t.ppf(q=0.975, df=df)
        t, p = ab_tools.is_significant_continuous(
            n1=n1,
            n2=n2,
            x1=203,
            x2=203,
            var1=var1,
            var2=var2,
            sig_level=0.05,
            tail="two_sided",
        )
        assert t_crit > abs(t)

    def test_significant_continuous_ab_test(self):
        ab_tools = ABTools()
        n1 = 100
        n2 = 100
        var1 = 56**2
        var2 = 112**2
        df = (var1 / n1 + var2 / n2) ** 2 / (
            (var1 / n1) ** 2 / (n1 - 1) + (var2 / n2) ** 2 / (n2 - 1)
        )
        t_crit = stats.t.ppf(q=0.975, df=df)
        t, p = ab_tools.is_significant_continuous(
            n1=n1,
            n2=n2,
            x1=250,
            x2=200,
            var1=var1,
            var2=var2,
            sig_level=0.05,
            tail="two_sided",
        )
        assert t_crit < abs(t)
