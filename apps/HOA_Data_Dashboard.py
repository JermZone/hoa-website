import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="HOA Dashboard", layout="wide")

def resolve_path(filename: str) -> Path | None:
    candidates = [
        Path("/data")/filename,
        Path.cwd()/filename,
        Path(__file__).parent/filename,
        Path(__file__).parent.parent/"data"/filename,
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

CHECKING_FILE = resolve_path("categorized_checking.csv")
SAVINGS_FILE = resolve_path("HOA Savings History.csv")

@st.cache_data
def load_data():
    if CHECKING_FILE is None:
        st.error("categorized_checking.csv not found. Tried: /data, CWD, script dir, ../data")
        st.stop()
    if not CHECKING_FILE.exists():
        st.error("categorized_checking.csv not found.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    df_checking = pd.read_csv(CHECKING_FILE)
    df_checking["Post Date"] = pd.to_datetime(df_checking["Post Date"])
    df_checking["Month"] = df_checking["Post Date"].dt.to_period("M").astype(str)
    df_checking["Amount"] = pd.to_numeric(df_checking["Amount"], errors="coerce")
    df_checking["Balance"] = pd.to_numeric(df_checking.get("Balance", 0), errors="coerce")

    if SAVINGS_FILE and SAVINGS_FILE.exists():
        df_savings = pd.read_csv(SAVINGS_FILE)
        df_savings["Post Date"] = pd.to_datetime(df_savings["Post Date"])
        df_savings = df_savings[["Post Date", "Balance"]].dropna()
        df_savings = df_savings.rename(columns={"Balance": "Savings Balance"})
    else:
        df_savings = None
        st.info("Savings file not found; skipping savings charts.")

    df_bal = df_checking[["Post Date", "Balance"]].rename(columns={"Balance": "Checking Balance"})
    if df_savings is not None:
        df_merged = pd.merge(df_bal, df_savings, on="Post Date", how="outer").sort_values("Post Date")
        df_merged["Checking Balance"] = df_merged["Checking Balance"].fillna(method="ffill")
        df_merged["Savings Balance"] = df_merged["Savings Balance"].fillna(method="ffill")
        df_merged["Total Balance"] = df_merged["Checking Balance"] + df_merged["Savings Balance"]
    else:
        df_merged = df_bal.copy()
        df_merged["Savings Balance"] = 0
        df_merged["Total Balance"] = df_merged["Checking Balance"]

    return df_checking, df_savings, df_merged

df, df_savings, df_balances = load_data()

st.title("🏛️ HOA Dashboard")
st.caption("Visualize categorized HOA checking and savings account data")

if df.empty:
    st.stop()

# --- Data Preview
with st.expander("📄 Loaded Data Preview", expanded=False):
    st.markdown(f"**Total Rows Loaded:** {len(df):,}")
    st.dataframe(df, use_container_width=True, hide_index=True)

categories = sorted(df["Category"].dropna().unique())
vendors = sorted(df["Vendor"].dropna().unique())

# --- Sidebar Filters
with st.sidebar:
    st.header("Filters")

    min_date = df["Post Date"].min().date()
    max_date = df["Post Date"].max().date()

    start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

    if start_date > end_date:
        st.warning("Start date must be before end date.")
        st.stop()

    date_label = f"{start_date.strftime('%b %Y')} – {end_date.strftime('%b %Y')}"

    selected_categories = st.multiselect("Categories", categories, default=categories)
    selected_vendors = st.multiselect("Vendors", vendors, default=vendors)
    exclude_transfers = st.checkbox("Exclude Transfers", value=True)

    if exclude_transfers:
        excluded_categories = sorted([
            cat for cat in selected_categories
            if pd.notna(cat) and "transfer" in cat.lower()
        ])
        if excluded_categories:
            st.markdown("Excluded Categories:")
            st.markdown("\n".join([f"- {cat}" for cat in excluded_categories]))
        else:
            st.markdown("_No categories matched 'transfer'_")

# --- Filtered Data
filtered_df = df[
    (df["Post Date"] >= pd.to_datetime(start_date)) &
    (df["Post Date"] <= pd.to_datetime(end_date))
]
filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]
filtered_df = filtered_df[filtered_df["Vendor"].isin(selected_vendors)]
if exclude_transfers:
    filtered_df = filtered_df[~filtered_df["Category"].str.contains("transfer", case=False, na=False)]

filtered_bal = df_balances[
    (df_balances["Post Date"] >= pd.to_datetime(start_date)) &
    (df_balances["Post Date"] <= pd.to_datetime(end_date))
]

# --- Balance Chart
st.subheader("💳 Balance Over Time")

fig_bal = go.Figure()
fig_bal.add_trace(go.Scatter(x=filtered_bal["Post Date"], y=filtered_bal["Checking Balance"],
                             mode="lines", name="Checking", line=dict(color="royalblue")))
fig_bal.add_trace(go.Scatter(x=filtered_bal["Post Date"], y=filtered_bal["Savings Balance"],
                             mode="lines", name="Savings", line=dict(color="green")))
fig_bal.add_trace(go.Scatter(x=filtered_bal["Post Date"], y=filtered_bal["Total Balance"],
                             mode="lines", name="Total", line=dict(color="orange")))

fig_bal.update_layout(
    title="Combined Account Balances",
    xaxis_title="Date",
    yaxis_title="Balance ($)",
    hovermode="x unified",
    legend_title="Accounts",
    template="plotly_white",
    yaxis_tickprefix="$",
    yaxis_tickformat=","
)

st.plotly_chart(fig_bal, use_container_width=True)

# --- Expenses Only
expenses = filtered_df[filtered_df["Amount"] < 0].copy()
expenses["Amount"] = expenses["Amount"].abs()

# --- Total Spent by Month
st.subheader("💰 Total Spent by Month")

monthly_spent = expenses.groupby("Month")["Amount"].sum().reset_index()
fig_spent = px.bar(monthly_spent, x="Month", y="Amount",
                   title=f"Total Spent per Month ({date_label})")
fig_spent.update_layout(
    yaxis_tickprefix="$",
    yaxis_tickformat=",",
    yaxis_title="Total Spent"
)
st.plotly_chart(fig_spent, use_container_width=True)

total_spent = expenses["Amount"].sum()
st.markdown(f"**Total Spent from {date_label}:** ${total_spent:,.2f}")

with st.expander("📋 Show Monthly Totals Table", expanded=False):
    monthly_spent["Amount"] = monthly_spent["Amount"].map("${:,.2f}".format)
    st.dataframe(monthly_spent.rename(columns={"Month": "Month", "Amount": "Total Spent"}), use_container_width=True)

# --- Deposits by Month
st.subheader("🏦 Deposits by Month")

monthly_deposits = filtered_df[filtered_df["Amount"] > 0].copy()
monthly_deposits["Month"] = monthly_deposits["Post Date"].dt.to_period("M").astype(str)
deposits_by_month = monthly_deposits.groupby("Month")["Amount"].sum().reset_index()

fig_deposits = px.bar(deposits_by_month, x="Month", y="Amount",
                      title=f"Total Deposits per Month ({date_label})")
fig_deposits.update_layout(
    yaxis_tickprefix="$",
    yaxis_tickformat=",",
    yaxis_title="Total Deposits"
)
st.plotly_chart(fig_deposits, use_container_width=True)

total_deposits = deposits_by_month["Amount"].sum()
st.markdown(f"**Total Deposits from {date_label}:** ${total_deposits:,.2f}")

with st.expander("📋 Show Monthly Deposits Table", expanded=False):
    deposits_by_month["Amount"] = deposits_by_month["Amount"].map("${:,.2f}".format)
    st.dataframe(deposits_by_month.rename(columns={"Month": "Month", "Amount": "Total Deposits"}),
                 use_container_width=True)

# --- Monthly Spending by Category
st.subheader("📅 Monthly Spending by Category")
pivot = expenses.groupby(["Month", "Category"])["Amount"].sum().reset_index()
fig1 = px.line(pivot, x="Month", y="Amount", color="Category", markers=True,
               title=f"Monthly Spending by Category ({date_label})")
fig1.update_layout(
    hovermode="x unified",
    yaxis_title="Amount",
    yaxis_tickprefix="$",
    yaxis_tickformat=","
)
st.plotly_chart(fig1, use_container_width=True)

# --- Spending by Vendor
st.subheader("🏷 Total Spending by Vendor")
vendor_totals = expenses.groupby("Vendor")["Amount"].sum().reset_index().sort_values("Amount", ascending=False)
fig2 = px.bar(vendor_totals, x="Vendor", y="Amount",
              title=f"Total Spending by Vendor ({date_label})")
fig2.update_layout(
    yaxis_tickprefix="$",
    yaxis_tickformat=","
)
st.plotly_chart(fig2, use_container_width=True)

# --- Download CSV
st.subheader("📥 Download Filtered Transactions")
csv_data = filtered_df.sort_values("Post Date")[[
    "Post Date", "Description", "Amount", "Balance",
    "Vendor", "Auto Vendor", "Category", "Auto Category"
]].reset_index(drop=True)

st.download_button("💾 Download CSV", data=csv_data.to_csv(index=False),
                   file_name="filtered_transactions.csv", mime="text/csv")

# --- Detailed Table
st.subheader("📄 Detailed Transactions")
st.dataframe(csv_data)
