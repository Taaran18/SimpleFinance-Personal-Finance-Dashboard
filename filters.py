import pandas as pd


def filter_transactions(df, date_range, selected_category, search_text):
    filtered_df = df.copy()
    filtered_df = filtered_df[
        (filtered_df["Date"] >= pd.to_datetime(date_range[0]))
        & (filtered_df["Date"] <= pd.to_datetime(date_range[1]))
    ]
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["Category"] == selected_category]
    if search_text:
        filtered_df = filtered_df[
            filtered_df["Details"].str.contains(search_text, case=False, na=False)
        ]
    return filtered_df


def add_balance_columns(filtered_df):
    filtered_df = filtered_df.sort_values("Date")
    filtered_df["SignedAmount"] = filtered_df.apply(
        lambda row: (
            row["Amount"] if row["Debit/Credit"] == "Credit" else -row["Amount"]
        ),
        axis=1,
    )
    filtered_df["Balance"] = filtered_df["SignedAmount"].cumsum()
    return filtered_df
