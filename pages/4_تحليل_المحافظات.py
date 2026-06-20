from auth import check_login, show_logo

check_login()
show_logo()

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data

st.set_page_config(
    page_title="Heatmap المخزون",
    page_icon="🔥 Annotation 2026-03-11 213816.png",
    layout="wide"
)

col1, col2 = st.columns([1,5])
with col1:
    st.image(
        "Annotation 2026-03-11 213816.png",
        width=50
    )

with col2:
    st.title("🔥 تحليل المحافظات ")



st.divider()

df = load_data()

# ==================================
# تنظيف البيانات
# ==================================

for col in [
    "رصيد البداية",
    "الوارد",
    "المنصرف",
    "المتبقي"
]:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)

# ==================================
# الفلاتر
# ==================================

c1,c2,c3,c4 = st.columns(4)

with c1:

    year = st.selectbox(
        "السنة",
        ["الكل"] +
        sorted(
            df["السنة"]
            .dropna()
            .unique()
            .tolist()
        )
    )

with c2:

    month = st.selectbox(
        "الشهر",
        ["الكل"] +
        sorted(
            df["الشهر"]
            .dropna()
            .unique()
            .tolist()
        )
    )

with c3:

    source = st.selectbox(
        "المصدر",
        ["الكل"] +
        sorted(
            df["المصدر"]
            .dropna()
            .unique()
            .tolist()
        )
    )

with c4:

    critical_only = st.checkbox(
        "الأصناف الحرجة فقط"
    )

filtered = df.copy()

if year != "الكل":
    filtered = filtered[
        filtered["السنة"] == year
    ]

if month != "الكل":
    filtered = filtered[
        filtered["الشهر"] == month
    ]

if source != "الكل":
    filtered = filtered[
        filtered["المصدر"] == source
    ]

# ==================================
# Pivot
# ==================================

pivot = filtered.pivot_table(
    index="الصنف",
    columns="الفرع",
    values="المتبقي",
    aggfunc="sum",
    fill_value=0
)

if critical_only:

    pivot = pivot[
        pivot.min(axis=1) <= 10
    ]

# ==================================
# KPIs
# ==================================

st.divider()

k1,k2,k3,k4 = st.columns(4)

k1.metric(
    "عدد الأصناف",
    len(pivot)
)

k2.metric(
    "عدد الفروع",
    len(pivot.columns)
)

k3.metric(
    "أصناف حرجة",
    len(
        pivot[
            pivot.min(axis=1) <= 10
        ]
    )
)

k4.metric(
    "إجمالي الرصيد",
    int(
        pivot.sum().sum()
    )
)

# ==================================
# Heatmap
# ==================================

st.divider()

st.subheader("🔥 خريطة توزيع المخزون")


styled = (
    pivot.style
    .format("{:.0f}")
    .background_gradient(cmap="RdYlGn")
)

st.dataframe(
    styled,
    use_container_width=True,
    height=600
)

# ==================================
# أكثر الأصناف خطورة
# ==================================

st.divider()

st.subheader("🚨 أقل الأصناف رصيداً")

lowest_items = (
    filtered
    .groupby("الصنف")["المتبقي"]
    .sum()
    .reset_index()
    .sort_values(
        "المتبقي"
    )
    .head(20)
)

st.dataframe(
    lowest_items,
    use_container_width=True
)

# ==================================
# جدول ملون
# ==================================

st.divider()



