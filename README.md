# 📊 NLP Sales Data Assistant

An interactive natural-language data analysis dashboard built with **Python**, **Streamlit**, **Pandas**, and **Plotly**. Users can query the Superstore retail dataset in plain English to generate formatted summary tables and interactive visualizations without writing SQL or spreadsheet formulas.

## ✨ Features
- **Natural Language Querying:** Uses fuzzy string matching (`fuzzywuzzy`) to map user questions to analytical functions.
- **Interactive Visualizations:** Generates dynamic Plotly bar and donut charts for yearly, regional, and category sales.
- **KPI & Financial Breakdowns:** Computes yearly/monthly revenue, segment profitability, top-performing products, and underperforming categories.
- **One-Click Sample Prompts:** Sidebar selector for quick exploration and demos.

## 🗂️ Project Structure
```text
nlp-sales-assistant/
├── app.py               # Streamlit web interface
├── ai_agent.py          # Data aggregation, charts, and NLP intent routing
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
└── data/
    └── superstore.csv   # Superstore dataset
```

## 🚀 How to Run Locally

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/nlp-sales-assistant.git
   cd nlp-sales-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the application**
   ```bash
   python -m streamlit run app.py
   ```
