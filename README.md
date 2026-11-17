# 📊 Universal NLP Data Explorer

An interactive, zero-API-key data analysis web application built with **Python**, **Streamlit**, **Pandas**, and **Plotly**. Upload **any CSV or Excel dataset** (or explore the built-in Superstore retail dataset) to automatically profile columns, generate dynamic prompts, and query data in plain English.

🚀 **[Try the Live App on Streamlit Cloud](https://nlp-sales-data-assistant.streamlit.app/#nlp-sales-data-assistant)**

## ✨ Key Features
- **Universal File Upload:** Supports `.csv`, `.xlsx`, and `.xls` files with automatic encoding fallback and schema detection.
- **Auto-Generated Sample Prompts:** Dynamically inspects uploaded columns (numeric, categorical, and datetime) to suggest relevant queries automatically.
- **Natural-Language Aggregations & Charts:** Supports `sum`, `average`, `top N`, `lowest N`, time trends, missing-value audits, correlation heatmaps, and interactive Plotly charts (`bar`, `pie`/`donut`, `line`).
- **Instant Dataset Profiling:** Displays row counts, column counts, numeric field detection, missing cell metrics, and a live schema preview.

## 🗂️ Project Structure
```text
nlp-sales-data-assistant/
├── app.py               # Streamlit UI with file uploader, KPI cards, and chart viewer
├── ai_agent.py          # Schema detector, dynamic prompt builder, and NLP query engine
├── requirements.txt     # Python dependencies (including openpyxl for Excel support)
├── README.md            # Project documentation
└── data/
    └── superstore.csv   # Default sample dataset
```

## 🚀 Run Locally

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the app**
   ```bash
   python -m streamlit run app.py
   ```
