import streamlit as st
from ai_agent import ai_agent, query_map

st.set_page_config(
    page_title="NLP Sales Data Assistant",
    page_icon="📊",
    layout="centered",
)

st.title("📊 NLP Sales Data Assistant")
st.markdown(
    "Ask questions about the Superstore sales dataset in plain English to generate instant tables and interactive charts."
)

with st.sidebar:
    st.header("💡 Sample Prompts")
    st.markdown("Click or type any of these queries:")
    sample_queries = [
        "Yearly sales",
        "Yearly sales chart",
        "Profit by segment",
        "Show me top products",
        "Category sales chart",
        "Regional sales chart",
        "Monthly sales",
        "Which category sold least?",
    ]
    selected_sample = st.selectbox("Choose a sample query:", [""] + sample_queries)
    st.divider()
    st.caption(f"Supported intents: {len(query_map)}")

query = st.text_input(
    "📝 Ask your question",
    value=selected_sample,
    placeholder="e.g., Show me profit by segment or yearly sales chart",
)

if query:
    with st.spinner("Analyzing data..."):
        result = ai_agent(query)

    st.subheader("Result")
    if isinstance(result, str):
        st.warning(result)
    elif hasattr(result, "to_plotly_json"):  # Plotly figure
        st.plotly_chart(result, use_container_width=True)
    else:
        st.dataframe(result, use_container_width=True, hide_index=True)