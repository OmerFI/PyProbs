import unittest
from PyProbs import Probability as pr


class Test(unittest.TestCase):
    def setUp(self):
        self.p = pr()
        self.true_or_false = [True, False]

    def test_prob(self):
        self.assertIn(pr.Prob(1/2), self.true_or_false)
        self.assertIn(pr.Prob(0.778), self.true_or_false)
        self.assertIn(pr.Prob("25%"), self.true_or_false)
        self.assertEqual(len(pr.Prob("25%", num=5)), 5)

    def test_iprob(self):
        self.assertIn(self.p.iProb(1/5), self.true_or_false)

        result = self.p.iProb(3/5, 0.15, num=2)
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 2)
        self.assertEqual(len(result[1]), 2)

        self.p.set_constant(0.5)
        self.assertEqual(0.5, self.p._constant)
        self.assertIn(self.p.iProb(), self.true_or_false)

        self.assertEqual(len(self.p.history.get(3/5, None)), 2)
        self.assertIn(self.p.history.get(3/5, None)[0], self.true_or_false)
        self.assertIn(self.p.history.get(1/5, None)[0], self.true_or_false)

        self.assertEqual(self.p.count_values(which="all")[True] + 
                         self.p.count_values(which="all")[False] , 6)


if __name__ == "__main__":
    unittest.main()
