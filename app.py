import pandas as pd
import streamlit as st
import plotly.express as px
from analytics import demo_data, prepare, metrics, aggregate, insights, safe_sql_query

st.set_page_config(page_title="Prism | Business Intelligence", page_icon="💠", layout="wide")
st.title("💠 Prism")
st.caption("Business intelligence workspace · transparent analytics with an optional AI-assisted narrative")
st.info("The built-in dataset is **synthetic demo data**. Uploaded CSV data is processed in-session; no server-side upload storage is implemented.")

with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    st.caption("Columns: date, merchant, category, amount; optional orders")
    st.subheader("AI narrative (optional)")
    ai_enabled = st.toggle("Enable AI narrative with OpenAI API", value=False)
    st.caption("Requires your own OPENAI_API_KEY in Streamlit secrets or environment. Data aggregates, not raw rows, are sent.")
try:
    raw = pd.read_csv(uploaded) if uploaded else demo_data()
    df = prepare(raw)
    if df.empty:
        st.error("No valid transactions found.")
        st.stop()
    categories = sorted(df["category"].unique().tolist())
    merchants = sorted(df["merchant"].unique().tolist())
    selected_categories = st.multiselect("Categories", categories, default=categories)
    selected_merchants = st.multiselect("Merchants", merchants, default=merchants)
    subset = df[df["category"].isin(selected_categories) & df["merchant"].isin(selected_merchants)]
    if subset.empty:
        st.warning("No rows match the selected filters.")
        st.stop()

    kpi = metrics(subset)
    a, b, c, d = st.columns(4)
    a.metric("Sales", f"${kpi['sales']:,.2f}")
    b.metric("Orders", f"{kpi['orders']:,}")
    c.metric("Average order value", f"${kpi['average_order_value']:,.2f}")
    d.metric("Merchants", kpi["merchants"])
    left, right = st.columns(2)
    with left:
        trend = aggregate(subset, "W-MON")
        st.plotly_chart(px.line(trend, x="date", y="sales", markers=True,
                                title="Weekly revenue"), use_container_width=True)
    with right:
        cat = safe_sql_query(subset)
        st.plotly_chart(px.bar(cat, x="category", y="sales",
                               title="Revenue by category"), use_container_width=True)
    st.subheader("Explain the data")
    observations = insights(subset)
    for observation in observations:
        st.write("• " + observation)
    st.caption("The observations above use reproducible statistical rules, not an AI model.")

    if ai_enabled:
        import os
        api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", "")) if hasattr(st, "secrets") else os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            st.warning("Add OPENAI_API_KEY to Streamlit secrets or your environment to use AI narrative.")
        else:
            if st.button("Generate AI narrative"):
                try:
                    from openai import OpenAI
                    summary = "\n".join(observations)
                    response = OpenAI(api_key=api_key).responses.create(
                        model="gpt-4.1-mini",
                        instructions="Summarise business metrics conservatively. Do not invent causes or future results. Note data limitations.",
                        input=f"Summarise these aggregate metrics only, under 150 words:\n{summary}",
                        max_output_tokens=240,
                    )
                    st.markdown(response.output_text)
                    st.caption("AI-generated narrative. Check claims against the charts.")
                except Exception as exc:
                    st.error("The optional AI request failed. Check your API key, account permissions and network access.")
    st.subheader("SQL-powered category summary")
    st.dataframe(safe_sql_query(subset), use_container_width=True)
    st.download_button("Download filtered rows (CSV)", subset.to_csv(index=False),
                       file_name="prism_filtered.csv", mime="text/csv")
    with st.expander("Data quality and limitations"):
        st.write(f"Rows imported: {len(raw):,}; valid rows after cleaning: {len(df):,}.")
        st.write("Missing/invalid dates and amounts, negative sales and negative order counts are removed. "
                 "The default amount currency is not assumed. Only use a single currency per upload. "
                 "This app does not implement enterprise permissions, persistent uploads or a production database.")
except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as exc:
    st.error(f"Unable to process CSV: {exc}")
