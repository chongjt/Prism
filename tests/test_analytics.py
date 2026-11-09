import unittest
import pandas as pd
from analytics import demo_data, prepare, metrics, safe_sql_query, insights

class TestAnalytics(unittest.TestCase):
    def test_demo(self):
        df = prepare(demo_data())
        self.assertGreater(len(df), 100)
        self.assertGreater(metrics(df)["sales"], 0)

    def test_missing_column(self):
        with self.assertRaises(ValueError):
            prepare(pd.DataFrame({"amount": [1]}))

    def test_invalid_values(self):
        df = pd.DataFrame({"date": ["2026-01-01", "invalid", "2026-01-02"],
                           "merchant": ["A", "B", "A"], "category": ["Food"] * 3,
                           "amount": [10, 5, -2], "orders": [2, 1, 1]})
        result = prepare(df)
        self.assertEqual(len(result), 1)
        self.assertEqual(metrics(result)["average_order_value"], 5)

    def test_query_and_insights(self):
        df = prepare(demo_data())
        summary = safe_sql_query(df, "Food")
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary.loc[0, "category"], "Food")
        self.assertGreaterEqual(len(insights(df)), 2)

if __name__ == "__main__":
    unittest.main()
