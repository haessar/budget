import unittest

import classify_transactions

class ExamplesMixin(object):
    true_categories = ['weekend_commute', 'dining_out', 'pubs_bars', 'concerts', 'street_food']
    true_starts_input = 'pubs'
    true_within_input = 'bars'
    not_in_true_categories_input = 'zoo'
    multi_starts_categories = ['cat1', 'cat2']
    multi_within_categories = ['first_cat', 'second_cat']
    multi_input = 'cat'

class CorrectCategoryTest(unittest.TestCase, ExamplesMixin):
    def setUp(self):
        self.correct_category_true = lambda x: classify_transactions.correct_category(x, self.true_categories)
        self.correct_category_multi = lambda x: classify_transactions.correct_category(self.multi_input, x)
    def test_bad_input(self):
        with self.assertRaisesRegexp(ValueError, 'not recognised'):
            self.correct_category_true(self.not_in_true_categories_input)
    def test_good_input(self):
        self.assertEqual(
            self.correct_category_true(self.true_starts_input),
            [x for x in self.true_categories if x.startswith(self.true_starts_input)][0]
        )
        self.assertEqual(
            self.correct_category_true(self.true_within_input),
            [x for x in self.true_categories if self.true_within_input in x][0]
        )
    def test_multiple_categories(self):
        with self.assertRaisesRegexp(ValueError, 'narrow down'):
            self.correct_category_multi(self.multi_starts_categories)
            self.correct_category_multi(self.multi_within_categories)
