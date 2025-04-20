import json
import os
import pandas as pd
import streamlit as st

category_file = "categories.json"


def load_categories():
    if os.path.exists(category_file):
        with open(category_file, "r") as f:
            return json.load(f)
    return {
        "Uncategorized": [],
        "Food": [],
        "Transport": [],
        "Shopping": [],
        "Utilities": [],
        "Health": [],
        "Entertainment": [],
        "Education": [],
        "Other": [],
    }


def save_categories(categories):
    with open(category_file, "w") as f:
        json.dump(categories, f)


def categorize_transactions(df, categories):
    df["Category"] = "Uncategorized"
    for category, keywords in categories.items():
        if category == "Uncategorized" or not keywords:
            continue
        lowered_keywords = [keyword.lower().strip() for keyword in keywords]
        for idx, row in df.iterrows():
            details = row["Details"].lower().strip()
            if details in lowered_keywords:
                df.at[idx, "Category"] = category
    return df


def load_transactions(file, categories):
    try:
        df = pd.read_csv(file)
        df.columns = [col.strip() for col in df.columns]
        df["Amount"] = df["Amount"].astype(str).str.replace(",", "").astype(float)
        df["Date"] = pd.to_datetime(df["Date"], format="%d %b %Y")
        return categorize_transactions(df, categories)
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None


def add_keyword_to_category(categories, category, keyword):
    keyword = keyword.strip()
    if keyword and keyword not in categories[category]:
        categories[category].append(keyword)
        save_categories(categories)
        return True
    return False
