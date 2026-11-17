import streamlit as st
from ai_agent import (
    ai_agent,
    detect_column_types,
    generate_sample_prompts,
    load_dataset,
)

st.set_page_config(
    page_title="Universal NLP Data Explorer",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Universal NLP Data Explorer")
st.markdown(
    "Upload **any CSV or Excel dataset** (or explore the built-in Superstore dataset) and ask questions in plain English—no API key or SQL required."
)

# Sidebar: File Upload & Sample Prompts
with st.sidebar:
    st.header("📂 1. Data Source")
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        help="Leave empty to explore the built-in Superstore sample dataset.",
    )

    try:
        df, dataset_name = load_dataset(uploaded_file)
    except Exception as e:
        st.error(f"Could not read file: {e}")
        st.stop()

    col_types = detect_column_types(df.copy())
    sample_queries = generate_sample_prompts(col_types)

    st.divider()
    st.header("💡 2. Sample Queries")
    selected_sample = st.selectbox(
        "Pick a generated query for this dataset:",
        [""] + sample_queries,
    )
    st.caption(
        f"Detected **{len(col_types['numeric'])}** numeric, "
        f"**{len(col_types['categorical'])}** categorical, and "
        f"**{len(col_types['datetime'])}** date columns."
    )

# Top KPI Overview Cards
st.caption(f"Active Dataset: **{dataset_name}**")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Rows", f"{len(df):,}")
kpi2.metric("Total Columns", f"{len(df.columns)}")
kpi3.metric("Numeric Fields", f"{len(col_types['numeric'])}")
kpi4.metric("Missing Cells", f"{int(df.isnull().sum().sum()):,}")

with st.expander("🔍 Preview Dataset & Column Schema", expanded=False):
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)

st.divider()

# Natural Language Query Section
query = st.text_input(
    "📝 Ask a question about your data",
    value=selected_sample,
    placeholder="e.g., Total Sales by Category, Top 5 Product Name by Profit, or Show dataset summary",
)

if query:
    with st.spinner("Analyzing dataset..."):
        result = ai_agent(query, df)

    st.subheader("Result")
    if isinstance(result, str):
        st.warning(result)
    elif hasattr(result, "to_plotly_json"):
        st.plotly_chart(result, use_container_width=True)
    else:
        st.dataframe(result, use_container_width=True, hide_index=True)
