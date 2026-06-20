import pandas as pd
import streamlit as st

SHEET_ID = "14pMYWjrkeOtKW5eE1ldE_MhbXDd9PiInN9jZCl9gPLQ"
GID = "2007220420"

@st.cache_data(ttl=300)
def load_data():

    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

    df = pd.read_csv(url)

    # تنظيف أسماء الأعمدة
    df.columns = df.columns.str.strip()

    # تحويل الأعمدة الرقمية
    numeric_cols = [
        "رصيد البداية",
        "الوارد",
        "المنصرف",
        "المتبقي"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            ).fillna(0)

    return df