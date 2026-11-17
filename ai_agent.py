from pathlib import Path
import re
import pandas as pd
import plotly.express as px
from fuzzywuzzy import process

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = BASE_DIR / "data" / "superstore.csv"


def load_dataset(uploaded_file=None) -> tuple[pd.DataFrame, str]:
    """Loads an uploaded CSV/Excel file or falls back to the built-in Superstore dataset."""
    if uploaded_file is not None:
        filename = uploaded_file.name
        if filename.lower().endswith(".csv"):
            try:
                df = pd.read_csv(uploaded_file)
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding="latin1")
        else:
            df = pd.read_excel(uploaded_file)
        return df, filename

    df = pd.read_csv(DEFAULT_DATA_PATH, encoding="latin1")
    return df, "Sample: Superstore Sales (superstore.csv)"


def detect_column_types(df: pd.DataFrame) -> dict:
    """Automatically categorizes columns into numeric, categorical, and datetime."""
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime64[ns]", "datetime"]).columns.tolist()

    # Attempt to detect date-like string columns
    for col in df.select_dtypes(include=["object", "string"]).columns:
        if any(keyword in col.lower() for keyword in ["date", "time", "year", "month"]):
            parsed = pd.to_datetime(df[col], errors="coerce")
            if parsed.notna().mean() > 0.7:
                df[col] = parsed
                datetime_cols.append(col)

    categorical_cols = [
        col
        for col in df.columns
        if col not in numeric_cols and col not in datetime_cols and df[col].nunique() <= 50
    ]
    all_text_cols = [
        col for col in df.columns if col not in numeric_cols and col not in datetime_cols
    ]

    return {
        "numeric": numeric_cols,
        "categorical": categorical_cols,
        "text": all_text_cols,
        "datetime": datetime_cols,
    }


def _match_column(query: str, candidates: list[str]) -> str | None:
    """Finds the best matching column name mentioned in the user's query."""
    if not candidates:
        return None
    q = query.lower()
    for col in candidates:
        if col.lower() in q:
            return col
    best_col, score = process.extractOne(q, candidates)
    return best_col if score >= 65 else None


def generate_sample_prompts(col_types: dict) -> list[str]:
    """Builds dynamic sample queries tailored to whatever dataset is currently loaded."""
    num_cols = col_types["numeric"]
    cat_cols = col_types["categorical"] or col_types["text"]
    date_cols = col_types["datetime"]

    prompts = ["Show dataset summary", "Show missing values"]

    if num_cols and cat_cols:
        num = num_cols[0]
        cat = cat_cols[0]
        prompts.append(f"Total {num} by {cat}")
        prompts.append(f"{num} by {cat} chart")
        prompts.append(f"Top 5 {cat} by {num}")
        prompts.append(f"Lowest {cat} by {num}")

    if len(num_cols) > 1 and len(cat_cols) > 1:
        prompts.append(f"Average {num_cols[1]} by {cat_cols[1]}")

    if num_cols and date_cols:
        prompts.append(f"{num_cols[0]} trend over time chart")

    return prompts


def ai_agent(query: str, df: pd.DataFrame):
    """Dynamic NLP query router that works on any uploaded CSV or Excel dataset."""
    if not query or not query.strip():
        return "Please enter a valid question."

    df = df.copy()
    col_types = detect_column_types(df)
    num_cols = col_types["numeric"]
    cat_cols = col_types["categorical"] or col_types["text"]
    date_cols = col_types["datetime"]

    q = query.lower().strip()
    wants_chart = any(word in q for word in ["chart", "plot", "graph", "visual", "pie", "bar", "line"])

    # 1. Dataset summary / statistics
    if any(word in q for word in ["summary", "describe", "overview", "stats", "statistics"]):
        if not num_cols:
            return df.describe(include="all").T.reset_index().rename(columns={"index": "Column"})
        summary = df[num_cols].describe().T[["count", "mean", "min", "50%", "max"]].round(2).reset_index()
        summary.columns = ["Column", "Count", "Mean", "Min", "Median", "Max"]
        return summary

    # 2. Missing values check
    if "missing" in q or "null" in q or "na" in q.split():
        missing = df.isnull().sum().reset_index()
        missing.columns = ["Column", "Missing Values"]
        missing["Missing (%)"] = ((missing["Missing Values"] / len(df)) * 100).round(2)
        return missing

    # 3. Correlation matrix
    if "correlation" in q or "corr" in q:
        if len(num_cols) < 2:
            return "At least two numeric columns are needed to compute correlations."
        corr = df[num_cols].corr().round(2)
        if wants_chart:
            return px.imshow(corr, text_auto=True, title="Numeric Feature Correlation Heatmap")
        return corr.reset_index().rename(columns={"index": "Feature"})

    # 4. Time trend analysis
    if any(word in q for word in ["trend", "over time", "yearly", "monthly", "timeline"]) and date_cols and num_cols:
        date_col = _match_column(q, date_cols) or date_cols[0]
        num_col = _match_column(q, num_cols) or num_cols[0]
        freq = "YE" if "yearly" in q else "ME"
        trend = (
            df.dropna(subset=[date_col])
            .set_index(date_col)[num_col]
            .resample(freq)
            .sum()
            .round(2)
            .reset_index()
        )
        trend.columns = [date_col, f"Total {num_col}"]
        if wants_chart or "trend" in q:
            return px.line(
                trend,
                x=date_col,
                y=f"Total {num_col}",
                title=f"{num_col} Trend Over Time",
                markers=True,
            )
        return trend

    # 5. Group-by aggregation (Top / Lowest / Average / Total / Count)
    if num_cols and cat_cols:
        num_col = _match_column(q, num_cols) or num_cols[0]
        # Prefer category columns matching the query; fall back to first categorical column
        cat_col = _match_column(q, cat_cols) or cat_cols[0]

        agg_func = "mean" if any(w in q for w in ["average", "avg", "mean"]) else "sum"
        agg_label = "Average" if agg_func == "mean" else "Total"

        grouped = (
            df.groupby(cat_col, dropna=False)[num_col]
            .agg(agg_func)
            .round(2)
            .reset_index()
        )
        metric_col = f"{agg_label} {num_col}"
        grouped.columns = [cat_col, metric_col]

        # Extract top/bottom N if specified (e.g., "top 5", "bottom 3", "least")
        top_match = re.search(r"(top|bottom|lowest|least)\s*(\d+)?", q)
        if top_match:
            direction = top_match.group(1)
            n = int(top_match.group(2)) if top_match.group(2) else 5
            ascending = direction in ["bottom", "lowest", "least"]
            grouped = grouped.sort_values(by=metric_col, ascending=ascending).head(n)
        else:
            grouped = grouped.sort_values(by=metric_col, ascending=False)

        if wants_chart:
            if "pie" in q or "donut" in q or len(grouped) <= 5:
                return px.pie(
                    grouped,
                    names=cat_col,
                    values=metric_col,
                    title=f"{metric_col} by {cat_col}",
                    hole=0.4,
                )
            return px.bar(
                grouped.head(15),
                x=cat_col,
                y=metric_col,
                title=f"{metric_col} by {cat_col}",
                text_auto=".2s",
                color=cat_col if len(grouped) <= 10 else None,
            )

        return grouped

    # 6. Fallback for categorical-only datasets (value counts)
    if cat_cols:
        cat_col = _match_column(q, cat_cols) or cat_cols[0]
        counts = df[cat_col].value_counts().reset_index()
        counts.columns = [cat_col, "Count"]
        if wants_chart:
            return px.bar(counts.head(15), x=cat_col, y="Count", title=f"Distribution of {cat_col}")
        return counts

    return (
        "I couldn't map that question to the dataset columns. "
        f"Available columns: {', '.join(df.columns)}"
    )
