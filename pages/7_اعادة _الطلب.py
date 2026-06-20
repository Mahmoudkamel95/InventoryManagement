from auth import check_login, show_logo

check_login()
show_logo()

import streamlit as st
import pandas as pd

from utils.reorder import reorder_engine
from utils.data_loader import load_data

st.set_page_config(
    page_title="نظام إعادة الطلب",
    layout="wide"
)

st.title("📦 نظام إعادة الطلب ")

df = load_data()

reorder = reorder_engine(df)

# -------------------------
# تنظيف
# -------------------------

reorder = reorder[
    reorder["كمية_الطلب_المقترحة"] > 0
]

# -------------------------
# KPIs
# -------------------------

st.divider()

# -------------------------
# فلاتر
# -------------------------

col1,col2,col3,col4,col5 = st.columns(5)

with col1:

    year = st.selectbox(
        "السنة",
        ["الكل"]
        +
        sorted(
            df["السنة"]
            .dropna()
            .unique()
            .tolist()
        )
    )

with col2:

    month = st.selectbox(
        "الشهر",
        ["الكل"]
        +
        sorted(
            df["الشهر"]
            .dropna()
            .unique()
            .tolist()
        )
    )

with col3:

    branch = st.selectbox(
        "الفرع",
        ["الكل"]
        +
        sorted(
            reorder["الفرع"]
            .dropna()
            .unique()
            .tolist()
        )
    )

with col4:

    source = st.selectbox(
        "المصدر",
        ["الكل"]
        +
        sorted(
            reorder["المصدر"]
            .dropna()
            .unique()
            .tolist()
        )
    )

with col5:

    item = st.selectbox(
        "الصنف",
        ["الكل"]
        +
        sorted(
            reorder["الصنف"]
            .dropna()
            .unique()
            .tolist()
        )
    )
 
 
st.divider()   
# -------------------------
# تطبيق الفلاتر
# -------------------------

filtered = reorder.copy()

if year != "الكل":
    filtered = filtered[
        filtered["السنة"] == year
    ]

if month != "الكل":
    filtered = filtered[
        filtered["الشهر"] == month
    ]

if branch != "الكل":
    filtered = filtered[
        filtered["الفرع"] == branch
    ]

if source != "الكل":
    filtered = filtered[
        filtered["المصدر"] == source
    ]

if item != "الكل":
    filtered = filtered[
        filtered["الصنف"] == item
    ]    
# -------------------------
# ترتيب حسب الأولوية
# -------------------------

filtered = filtered.sort_values(
    "كمية_الطلب_المقترحة",
    ascending=False
)

st.subheader("🚨 الأولويات القصوى")

top10 = filtered.head(10)

st.dataframe(
    top10,
    use_container_width=True
)

st.divider()
# -------------------------
# رسم بياني
# -------------------------

import plotly.express as px

st.subheader("📊 الاصناف الاكثر احتياج ")

chart_data = (
    filtered
    .groupby("الصنف")
    [
        "كمية_الطلب_المقترحة"
    ]
    .sum()
    .sort_values(
        ascending=False
    )
    .head(15)
    .reset_index()
)

fig = px.bar(
    chart_data,
    x="الصنف",
    y="كمية_الطلب_المقترحة",
    text="كمية_الطلب_المقترحة"
)

fig.update_traces(
    marker_color="#00695c",
    textposition="outside"
)

fig.update_layout(
    xaxis=dict(
        type="category",
        categoryorder="array",
        categoryarray=chart_data["الصنف"].tolist()  # يحافظ على الترتيب التنازلي اللي عملته بـ sort_values
    ),
    xaxis_title="الصنف",
    yaxis_title="كمية الطلب المقترحة",
    height=450
)

st.plotly_chart(fig, use_container_width=True)
st.divider()
# -------------------------
# الجدول الكامل
# -------------------------

st.subheader("📋 جدول إعادة الطلب")

st.dataframe(
    filtered,
    use_container_width=True
)

