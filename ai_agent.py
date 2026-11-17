import pandas as pd
import plotly.express as px
from fuzzywuzzy import process

# Load and prepare dataset
df = pd.read_csv("data/superstore.csv", encoding="latin1")
df["Order Date"] = pd.to_datetime(df["Order Date"])


def get_yearly_sales():
    yearly_sales = df.groupby(df["Order Date"].dt.year)["Sales"].sum().round(2).reset_index()
    yearly_sales.columns = ["Year", "Total Sales ($)"]
    return yearly_sales


def get_sales_by_category():
    categorical_sales = df.groupby("Category")["Sales"].sum().round(2).reset_index()
    categorical_sales.columns = ["Category", "Total Sales ($)"]
    return categorical_sales


def get_monthly_sales():
    monthly_sales = (
        df.groupby(df["Order Date"].dt.to_period("M"))["Sales"]
        .sum()
        .round(2)
        .reset_index()
    )
    monthly_sales["Order Date"] = monthly_sales["Order Date"].astype(str)
    monthly_sales.columns = ["Month", "Total Sales ($)"]
    return monthly_sales


def get_sales_by_region():
    regional_sales = df.groupby("Region")["Sales"].sum().round(2).reset_index()
    regional_sales.columns = ["Region", "Total Sales ($)"]
    return regional_sales


def get_top_products(n=5):
    top_products = (
        df.groupby("Product Name")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .round(2)
        .reset_index()
    )
    top_products.columns = ["Product Name", "Total Sales ($)"]
    return top_products


def get_least_selling_categories():
    least_sales = (
        df.groupby("Category")["Sales"]
        .sum()
        .sort_values(ascending=True)
        .round(2)
        .reset_index()
    )
    least_sales.columns = ["Category", "Total Sales ($)"]
    return least_sales


def get_profit_by_segment():
    # Fixed: Aggregates 'Profit' instead of 'Sales'
    profit_segment = df.groupby("Segment")["Profit"].sum().round(2).reset_index()
    profit_segment.columns = ["Segment", "Total Profit ($)"]
    return profit_segment


def get_yearly_sales_chart():
    yearly_sales = df.groupby(df["Order Date"].dt.year)["Sales"].sum().reset_index()
    yearly_sales.columns = ["Year", "Sales"]
    fig = px.bar(
        yearly_sales,
        x="Year",
        y="Sales",
        title="Total Sales by Year",
        text_auto=".2s",
        color_discrete_sequence=["#2E86AB"],
    )
    fig.update_layout(xaxis_type="category")
    return fig


def get_category_sales_chart():
    categorical_sales = df.groupby("Category")["Sales"].sum().reset_index()
    fig = px.pie(
        categorical_sales,
        names="Category",
        values="Sales",
        title="Sales Distribution by Category",
        hole=0.4,
    )
    return fig


def get_regional_sales_chart():
    regional_sales = df.groupby("Region")["Sales"].sum().reset_index()
    fig = px.bar(
        regional_sales,
        x="Region",
        y="Sales",
        title="Sales by Region",
        text_auto=".2s",
        color="Region",
    )
    return fig


query_map = {
    "yearly sales": get_yearly_sales,
    "category-wise sales": get_sales_by_category,
    "monthly sales": get_monthly_sales,
    "sales by region": get_sales_by_region,
    "top products": get_top_products,
    "least selling categories": get_least_selling_categories,
    "profit by segment": get_profit_by_segment,
    "yearly sales chart": get_yearly_sales_chart,
    "category sales chart": get_category_sales_chart,
    "regional sales chart": get_regional_sales_chart,
}


def ai_agent(query: str):
    if not query or not query.strip():
        return "Please enter a valid question."

    cleaned_query = query.lower().strip()
    best_match, score = process.extractOne(cleaned_query, list(query_map.keys()))

    if score >= 65:
        return query_map[best_match]()
    else:
        available = ", ".join(query_map.keys())
        return (
            "Sorry, I didn't understand that question. "
            f"Try asking about: {available}."
        )