from auth import check_login, show_logo

check_login()
show_logo()

import streamlit as st
import pandas as pd

from utils.data_loader import load_data

st.set_page_config(
    page_title=" إدارة المخزون",
    page_icon=r"C:\Users\WIN 10\Desktop\Inventory_System\Annotation 2026-03-11 213816.png",
    layout="wide"
)

# ==================================
# تحميل البيانات
# ==================================

df = load_data()

# ==================================
# تنظيف البيانات
# ==================================

numeric_cols = [
    "رصيد البداية",
    "الوارد",
    "المنصرف",
    "المتبقي"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(0)

# ==================================
# Header
# ==================================

col1, col2 = st.columns([1,5])

with col1:
    st.image(
        r"C:\Users\WIN 10\Desktop\Inventory_System\Annotation 2026-03-11 213816.png",
        width=50
    )

with col2:
    st.title(" إدارة مخزون الادوية بمحافظات اقليم شمال الصعيد")

st.divider()
# ==================================
# Filters
# ==================================

st.subheader("🔎 الفلاتر")

col1,col2,col3 = st.columns(3)

with col1:

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

with col2:

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

with col3:

    branch = st.selectbox(
        "الفرع",
        ["الكل"] +
        sorted(
            df["الفرع"]
            .dropna()
            .unique()
            .tolist()
        )
    )

col4,col5 = st.columns(2)

with col4:

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

with col5:

    item = st.selectbox(
        "الصنف",
        ["الكل"] +
        sorted(
            df["الصنف"]
            .dropna()
            .unique()
            .tolist()
        )
    )

st.divider()
# ==================================
# تطبيق الفلاتر
# ==================================

filtered = df.copy()

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




# ==================================
# KPIs
# ==================================

total_opening = int(filtered["رصيد البداية"].sum())
total_received = int(filtered["الوارد"].sum())
total_consumed = int(filtered["المنصرف"].sum())
total_remaining = int(filtered["المتبقي"].sum())

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "رصيد البداية",
    f"{total_opening:,}",
    border=True,
)

c2.metric(
    "الوارد",
    f"{total_received:,}",
    border=True
)

c3.metric(
    "المنصرف",
    f"{total_consumed:,}",
    border=True
)

c4.metric(
    "المتبقي",
    f"{total_remaining:,}",
    border=True
)

# ==================================
# مؤشرات إضافية
# ==================================

zero_stock = len(
    filtered[
        filtered["المتبقي"] <= 0
    ]
)

LOW_STOCK_LIMIT = 50
low_stock = len(
    filtered[
        (filtered["المتبقي"] > 0)
        &
        (filtered["المتبقي"] < LOW_STOCK_LIMIT)
    ]
)

branches = filtered["الفرع"].nunique()

items = filtered["الصنف"].nunique()

st.divider()

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "أصناف نافدة",
    zero_stock,border=True
)

c2.metric(
    "أصناف منخفضة",
    low_stock ,border=True
)

c3.metric(
    "عدد الفروع",
    branches,border=True
)

c4.metric(
    "عدد الأصناف",
    items ,border=True
)

# ==================================
# الرسومات
# ==================================

st.divider()

import plotly.express as px
import streamlit as st

# ===== أعلى الفروع استهلاكاً =====
top_branches = (
    filtered.groupby("الفرع")["المنصرف"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig1 = px.bar(
    top_branches,
    x="الفرع",
    y="المنصرف",
    title="🏥 أعلى الفروع استهلاكاً",
    text_auto=True
)

fig1.update_layout(
    xaxis_title="الفرع",
    yaxis_title="المنصرف"
)

st.plotly_chart(fig1, use_container_width=True)


# ===== أعلى الأصناف استهلاكاً =====
top_items = (
    filtered.groupby("الصنف")["المنصرف"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig2 = px.bar(
    top_items,
    x="الصنف",
    y="المنصرف",
    title="📦 أعلى الأصناف استهلاكاً",
    text_auto=True
)

fig2.update_layout(
    xaxis_title="الصنف",
    yaxis_title="المنصرف"
)

st.plotly_chart(fig2, use_container_width=True)

# ==================================
# تنبيهات
# ==================================

st.divider()

st.subheader("🚨 الأصناف النافدة")

critical = filtered[
    filtered["المتبقي"] <= 0
]

if len(critical):

    st.error(
        f"يوجد {len(critical)} سجل يحتاج تدخل فوري"
    )

    st.dataframe(
        critical[
            [
                "السنة",
                "الشهر",
                "الفرع",
                "الصنف",
                "المتبقي",
                "المصدر"
            ]
        ],
        use_container_width=True
    )

else:

    st.success(
        "لا توجد أصناف نافدة"
    )

# ==================================
# أقل الأصناف رصيداً
# ==================================

st.divider()

st.subheader("📉 أقل الأصناف رصيداً")

lowest_items = (
    filtered
    .groupby("الصنف")["المتبقي"]
    .sum()
    .reset_index()
    .sort_values("المتبقي")
    .head(15)
)

st.dataframe(
    lowest_items,
    use_container_width=True
)

# =====================
# 🔹 TREND ANALYSIS
# =====================
st.divider()
st.subheader("📈 حركة المخزون عبر الزمن")

trend = filtered.groupby("الشهر")[["الوارد", "المنصرف"]].sum()

st.line_chart(trend)

# ==================================
# البيانات الحالية
# ==================================

st.divider()

st.subheader("📋 البيانات الحالية")

st.dataframe(
    filtered,
    use_container_width=True
)

# ==================================
# Footer
# ==================================

st.divider()

st.info(
    f"عدد السجلات الحالية بعد الفلترة: {len(filtered):,}"
)