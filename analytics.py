"""Data preparation and transparent, rule-based analysis for Prism."""
import io
import sqlite3
import pandas as pd
import numpy as np


def demo_data():
    """Synthetic illustrative sales transactions (not real customers)."""
    rng = np.random.default_rng(17)
    days = pd.date_range("2026-01-01", periods=140, freq="D")
    rows = []
    for day in days:
        for merchant, category, base in [("Aurora Mart", "Retail", 1150),
                                          ("North Cafe", "Food", 550),
                                          ("Digital Den", "Technology", 1470)]:
            value = max(0, rng.normal(base * (1 + (day.dayofweek >= 5) * .18), base * .2))
            rows.append((day.date().isoformat(), merchant, category, round(value, 2), int(rng.integers(1, 40))))
    return pd.DataFrame(rows, columns=["date", "merchant", "category", "amount", "orders"])


def prepare(data):
    required = {"date", "merchant", "category", "amount"}
    absent = required - set(data.columns)
    if absent:
        raise ValueError("Missing required columns: " + ", ".join(sorted(absent)))
    df = data.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"].astype(str).str.replace(",", "", regex=False), errors="coerce")
    if "orders" not in df:
        df["orders"] = 1
    df["orders"] = pd.to_numeric(df["orders"], errors="coerce")
    df["merchant"] = df["merchant"].astype("string").str.strip()
    df["category"] = df["category"].astype("string").str.strip()
    df = df.dropna(subset=["date", "amount", "orders", "merchant", "category"])
    df = df[(df["amount"] >= 0) & (df["orders"] >= 0)
            & (df["merchant"] != "") & (df["category"] != "")]
    return df.sort_values("date").reset_index(drop=True)


def metrics(df):
    if df.empty:
        return {"sales": 0.0, "orders": 0, "average_order_value": 0.0, "merchants": 0}
    sales = float(df["amount"].sum())
    orders = int(df["orders"].sum())
    return {"sales": sales, "orders": orders,
            "average_order_value": sales / orders if orders else 0.0,
            "merchants": int(df["merchant"].nunique())}


def aggregate(df, period="MS"):
    return (df.set_index("date")["amount"].resample(period).sum()
            .rename("sales").reset_index())


def insights(df):
    """Deterministic summaries: do not claim these are AI-generated."""
    if df.empty:
        return ["No valid rows for analysis."]
    k = metrics(df)
    top = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    daily = df.set_index("date")["amount"].resample("D").sum()
    output = [f"Revenue across the selected data is ${k['sales']:,.2f} from {k['orders']:,} recorded orders.",
              f"The highest-revenue category is {top.index[0]} (${top.iloc[0]:,.2f})."]
    if len(daily) >= 14:
        earlier = float(daily.iloc[-14:-7].sum())
        recent = float(daily.iloc[-7:].sum())
        if earlier:
            output.append(f"Sales in the latest 7 days changed {100 * (recent / earlier - 1):+.1f}% versus the prior 7 days.")
        else:
            output.append("Prior-week sales were zero, so a percentage change cannot be calculated.")
    return output


def safe_sql_query(df, category=None):
    """Only pre-defined SELECT query; user input is always bound as a parameter."""
    with sqlite3.connect(":memory:") as connection:
        df.assign(date=df["date"].dt.strftime("%Y-%m-%d")).to_sql("transactions", connection, index=False)
        statement = ("SELECT category, ROUND(SUM(amount), 2) AS sales, SUM(orders) AS orders "
                     "FROM transactions WHERE (? IS NULL OR category = ?) "
                     "GROUP BY category ORDER BY sales DESC")
        return pd.read_sql_query(statement, connection, params=(category, category))
