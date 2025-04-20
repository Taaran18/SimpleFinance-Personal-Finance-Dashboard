import streamlit as st

st.set_page_config(page_title="Simple Finance App", page_icon="💰", layout="wide")

import plotly.express as px
from utils import (
    load_categories,
    save_categories,
    load_transactions,
    add_keyword_to_category,
)
from filters import filter_transactions, add_balance_columns
import pandas as pd


def dashboard():
    st.markdown(
        "<h1 style='text-align: center; color: #4F8BF9;'>💰 SimpleFinance: Personal Finance Dashboard</h1>",
        unsafe_allow_html=True,
    )

    if "categories" not in st.session_state:
        st.session_state.categories = load_categories()
    else:
        st.session_state.categories = load_categories()

    uploaded_file = st.file_uploader(
        "Upload your transaction CSV file",
        type=["csv"],
        help="Upload your bank statement in CSV format.",
    )

    if uploaded_file is not None:
        df = load_transactions(uploaded_file, st.session_state.categories)
        if df is not None:
            debits_df = df[df["Debit/Credit"] == "Debit"].copy()
            credits_df = df[df["Debit/Credit"] == "Credit"].copy()
            st.session_state.debits_df = debits_df.copy()
            st.session_state.credits_df = credits_df.copy()

            st.sidebar.header("🔎 Filters & Search")
            min_date = df["Date"].min()
            max_date = df["Date"].max()
            date_range = st.sidebar.date_input(
                "Select Date Range",
                [min_date, max_date],
                min_value=min_date,
                max_value=max_date,
            )
            category_options = ["All"] + list(st.session_state.categories.keys())
            selected_category = st.sidebar.selectbox(
                "Filter by Category", category_options
            )
            search_text = st.sidebar.text_input("Search Details")

            filtered_df = filter_transactions(
                df, date_range, selected_category, search_text
            )
            filtered_df = add_balance_columns(filtered_df)

            st.markdown("### 📈 Trends & Balance Overview")
            trend_period = st.radio(
                "Trend Period", ["Monthly", "Yearly"], horizontal=True
            )
            if trend_period == "Monthly":
                filtered_df["Period"] = (
                    filtered_df["Date"].dt.to_period("M").astype(str)
                )
            else:
                filtered_df["Period"] = filtered_df["Date"].dt.year.astype(str)
            trend_df = (
                filtered_df.groupby(["Period", "Debit/Credit"])["Amount"]
                .sum()
                .reset_index()
                .pivot(index="Period", columns="Debit/Credit", values="Amount")
                .fillna(0)
            )
            trend_df["Net"] = trend_df.get("Credit", 0) - trend_df.get("Debit", 0)
            st.line_chart(trend_df[["Debit", "Credit", "Net"]])

            st.markdown("### 💹 Running Balance")
            st.area_chart(filtered_df.set_index("Date")["Balance"])

            st.markdown("### 🏆 Top Transactions")
            top_n = st.slider("Show Top N", min_value=3, max_value=20, value=5)
            col_exp, col_pay = st.columns(2)
            with col_exp:
                st.markdown("#### Top Expenses")
                top_exp = (
                    filtered_df[filtered_df["Debit/Credit"] == "Debit"]
                    .sort_values("Amount", ascending=False)
                    .head(top_n)
                )
                st.dataframe(
                    top_exp[["Date", "Details", "Amount", "Category"]],
                    use_container_width=True,
                    hide_index=True,
                )
            with col_pay:
                st.markdown("#### Top Payments")
                top_pay = (
                    filtered_df[filtered_df["Debit/Credit"] == "Credit"]
                    .sort_values("Amount", ascending=False)
                    .head(top_n)
                )
                st.dataframe(
                    top_pay[["Date", "Details", "Amount", "Category"]],
                    use_container_width=True,
                    hide_index=True,
                )

            st.markdown("### 📂 Category Drilldown")
            drill_category = st.selectbox(
                "Select Category to Drilldown", category_options
            )
            if drill_category != "All":
                drill_df = filtered_df[filtered_df["Category"] == drill_category]
                st.dataframe(
                    drill_df[["Date", "Details", "Amount", "Debit/Credit"]],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.dataframe(
                    filtered_df[
                        ["Date", "Details", "Amount", "Category", "Debit/Credit"]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

            st.markdown("### ⬇️ Export Filtered Data")
            st.download_button(
                label="Download Filtered Data as CSV",
                data=filtered_df.to_csv(index=False).encode("utf-8"),
                file_name="filtered_transactions.csv",
                mime="text/csv",
            )

            if search_text:
                st.markdown(f"**Highlighted Results for:** `{search_text}`")
                highlight_df = filtered_df[
                    filtered_df["Details"].str.contains(
                        search_text, case=False, na=False
                    )
                ]
                st.dataframe(
                    highlight_df[
                        ["Date", "Details", "Amount", "Category", "Debit/Credit"]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

            tab1, tab2 = st.tabs(["Expenses (Debits)", "Payments (Credits)"])
            with tab1:
                new_category = st.text_input("New Category Name")
                add_button = st.button("Add Category")
                if add_button and new_category:
                    if new_category not in st.session_state.categories:
                        st.session_state.categories[new_category] = []
                        save_categories(st.session_state.categories)
                        st.rerun()
                st.subheader("Your Expenses")
                edited_df = st.data_editor(
                    st.session_state.debits_df[
                        ["Date", "Details", "Amount", "Category"]
                    ],
                    column_config={
                        "Date": st.column_config.DateColumn(
                            "Date", format="DD/MM/YYYY"
                        ),
                        "Amount": st.column_config.NumberColumn(
                            "Amount", format="%.2f AED"
                        ),
                        "Category": st.column_config.SelectboxColumn(
                            "Category", options=list(st.session_state.categories.keys())
                        ),
                    },
                    hide_index=True,
                    use_container_width=True,
                    key="category_editor",
                )
                save_button = st.button("Apply Changes", type="primary")
                if save_button:
                    for idx, row in edited_df.iterrows():
                        st.session_state.debits_df.at[idx, "Amount"] = row["Amount"]
                        st.session_state.debits_df.at[idx, "Category"] = row["Category"]
                        details = row["Details"]
                        add_keyword_to_category(
                            st.session_state.categories, row["Category"], details
                        )
                    df.update(st.session_state.debits_df)
                total_expenses = st.session_state.debits_df["Amount"].sum()
                total_income = st.session_state.credits_df["Amount"].sum()
                net_savings = total_income - total_expenses
                num_transactions = len(df)
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Expenses", f"{total_expenses:,.2f} AED")
                col2.metric("Total Income", f"{total_income:,.2f} AED")
                col3.metric("Net Savings", f"{net_savings:,.2f} AED")
                col4.metric("Transactions", num_transactions)
                st.subheader("Expense Summary")
                category_totals = (
                    st.session_state.debits_df.groupby("Category")["Amount"]
                    .sum()
                    .reset_index()
                )
                category_totals = category_totals.sort_values("Amount", ascending=False)
                st.dataframe(
                    category_totals,
                    column_config={
                        "Amount": st.column_config.NumberColumn(
                            "Amount", format="%.2f AED"
                        )
                    },
                    use_container_width=True,
                    hide_index=True,
                )
                chart_type = st.radio("Chart Type", ["Pie", "Bar"], horizontal=True)
                if chart_type == "Pie":
                    fig = px.pie(
                        category_totals,
                        values="Amount",
                        names="Category",
                        title="Expenses by Category",
                    )
                else:
                    fig = px.bar(
                        category_totals,
                        x="Category",
                        y="Amount",
                        title="Expenses by Category",
                        text_auto=".2s",
                    )
                st.plotly_chart(fig, use_container_width=True)
                st.subheader("Recurring Expenses")
                recurring = st.session_state.debits_df["Details"].value_counts()
                recurring = recurring[recurring > 1]
                if not recurring.empty:
                    st.dataframe(
                        st.session_state.debits_df[
                            st.session_state.debits_df["Details"].isin(recurring.index)
                        ][["Date", "Details", "Amount", "Category"]],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.write("No recurring expenses detected.")
                st.subheader("Anomalies (Large Expenses)")
                threshold = st.number_input(
                    "Anomaly Threshold (AED)",
                    min_value=0.0,
                    value=float(
                        st.session_state.debits_df["Amount"].mean()
                        + 2 * st.session_state.debits_df["Amount"].std()
                    ),
                )
                anomalies = st.session_state.debits_df[
                    st.session_state.debits_df["Amount"] > threshold
                ]
                if not anomalies.empty:
                    st.dataframe(
                        anomalies[["Date", "Details", "Amount", "Category"]],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.write("No anomalies detected.")
                st.download_button(
                    label="Download Expenses as CSV",
                    data=st.session_state.debits_df.to_csv(index=False).encode("utf-8"),
                    file_name="expenses.csv",
                    mime="text/csv",
                )
            with tab2:
                st.subheader("Your Payments")
                edited_credits_df = st.data_editor(
                    st.session_state.credits_df[
                        ["Date", "Details", "Amount", "Category"]
                    ],
                    column_config={
                        "Date": st.column_config.DateColumn(
                            "Date", format="DD/MM/YYYY"
                        ),
                        "Amount": st.column_config.NumberColumn(
                            "Amount", format="%.2f AED"
                        ),
                        "Category": st.column_config.SelectboxColumn(
                            "Category", options=list(st.session_state.categories.keys())
                        ),
                    },
                    hide_index=True,
                    use_container_width=True,
                    key="credit_category_editor",
                )
                save_credits_button = st.button("Apply Credit Changes", type="primary")
                if save_credits_button:
                    for idx, row in edited_credits_df.iterrows():
                        st.session_state.credits_df.at[idx, "Amount"] = row["Amount"]
                        st.session_state.credits_df.at[idx, "Category"] = row[
                            "Category"
                        ]
                        details = row["Details"]
                        add_keyword_to_category(
                            st.session_state.categories, row["Category"], details
                        )
                    df.update(st.session_state.credits_df)
                total_expenses = st.session_state.debits_df["Amount"].sum()
                total_income = st.session_state.credits_df["Amount"].sum()
                net_savings = total_income - total_expenses
                num_transactions = len(df)
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Expenses", f"{total_expenses:,.2f} AED")
                col2.metric("Total Income", f"{total_income:,.2f} AED")
                col3.metric("Net Savings", f"{net_savings:,.2f} AED")
                col4.metric("Transactions", num_transactions)
                st.subheader("Payments Summary")
                credit_category_totals = (
                    st.session_state.credits_df.groupby("Category")["Amount"]
                    .sum()
                    .reset_index()
                )
                credit_category_totals = credit_category_totals.sort_values(
                    "Amount", ascending=False
                )
                st.dataframe(
                    credit_category_totals,
                    column_config={
                        "Amount": st.column_config.NumberColumn(
                            "Amount", format="%.2f AED"
                        )
                    },
                    use_container_width=True,
                    hide_index=True,
                )
                chart_type2 = st.radio(
                    "Chart Type",
                    ["Pie", "Bar"],
                    horizontal=True,
                    key="credit_chart_type",
                )
                if chart_type2 == "Pie":
                    fig2 = px.pie(
                        credit_category_totals,
                        values="Amount",
                        names="Category",
                        title="Payments by Category",
                    )
                else:
                    fig2 = px.bar(
                        credit_category_totals,
                        x="Category",
                        y="Amount",
                        title="Payments by Category",
                        text_auto=".2s",
                    )
                st.plotly_chart(fig2, use_container_width=True)
                st.subheader("Recurring Payments")
                recurring_credits = st.session_state.credits_df[
                    "Details"
                ].value_counts()
                recurring_credits = recurring_credits[recurring_credits > 1]
                if not recurring_credits.empty:
                    st.dataframe(
                        st.session_state.credits_df[
                            st.session_state.credits_df["Details"].isin(
                                recurring_credits.index
                            )
                        ][["Date", "Details", "Amount", "Category"]],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.write("No recurring payments detected.")
                st.subheader("Anomalies (Large Payments)")
                threshold_credits = st.number_input(
                    "Anomaly Threshold (AED)",
                    min_value=0.0,
                    value=float(
                        st.session_state.credits_df["Amount"].mean()
                        + 2 * st.session_state.credits_df["Amount"].std()
                    ),
                    key="credit_anomaly",
                )
                anomalies_credits = st.session_state.credits_df[
                    st.session_state.credits_df["Amount"] > threshold_credits
                ]
                if not anomalies_credits.empty:
                    st.dataframe(
                        anomalies_credits[["Date", "Details", "Amount", "Category"]],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.write("No anomalies detected.")
                st.download_button(
                    label="Download Payments as CSV",
                    data=st.session_state.credits_df.to_csv(index=False).encode(
                        "utf-8"
                    ),
                    file_name="payments.csv",
                    mime="text/csv",
                )
