# Prism 💠 — AI-assisted Business Intelligence

An educational Streamlit dashboard supporting CSV upload, KPIs, category filtering, time-series charts, in-memory SQLite queries and deterministic descriptive insights. Optional model-generated narrative requires an API key and explicit user action.

**Demo data is synthetic.** Prism is a portfolio MVP, not production business intelligence software.

## Installation

Python 3.10+:

```bash
python -m venv .venv
pip install -r requirements.txt
streamlit run app.py
```

## CSV schema

Required: `date,merchant,category,amount`. Optional: `orders` (defaults to 1).

```csv
date,merchant,category,amount,orders
2026-01-01,Example Store,Retail,120.50,3
2026-01-02,Cafe Example,Food,46.00,2
```

Use a single currency. Invalid rows and negative amounts are removed.

## Optional AI narrative

Basic insights work offline without AI. For an optional OpenAI narrative:

```bash
pip install "openai>=1.55,<3"
```

Set `OPENAI_API_KEY` in your environment or Streamlit secrets. Toggle AI narrative and click **Generate AI narrative**. Only short, aggregate summaries (not raw rows) are sent, and API usage may incur charges. Never commit secret keys.

## Tests

```bash
python -m unittest discover -s tests -v
python -m compileall app.py analytics.py
```

## Code organisation

- `app.py`: interactive dashboard, upload, Plotly charts, user-controlled AI feature
- `analytics.py`: validation, KPIs, in-memory SQLite, deterministic insights
- `tests/test_analytics.py`: unit tests

## Limitations

No accounts, persistent uploads, production permissions, scheduled refresh, payment integration or multi-tenant isolation. SQLite runs in-memory to illustrate parameterised SQL. No real-world performance claims.

**AI use disclosure:** Code development involved AI assistance. Review, test, customise and understand the code before presenting it in an academic portfolio.
