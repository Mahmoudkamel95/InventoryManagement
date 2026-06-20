from auth import check_login, show_logo

check_login()
show_logo()

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data


col1, col2 = st.columns([1,5])


with col1:
    st.image(
        r"C:\Users\WIN 10\Desktop\Inventory_System\Annotation 2026-03-11 213816.png",
        width=50
    )

with col2:
    st.title("🔍 البحث عن صنف")




st.divider()

df = load_data()

# تنظيف الأعمدة الرقمية

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

# ----------------------------
# الفلاتر
# ----------------------------

col1,col2,col3 = st.columns(3)

with col1:

    item = st.selectbox(
        "الصنف",
        sorted(df["الصنف"].dropna().unique())
    )

with col2:

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

with col3:

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

col4,col5,col6 = st.columns(3)

with col4:

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

with col5:

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

with col6:

    stock_status = st.selectbox(
        "حالة المخزون",
        [
            "الكل",
            "نافد",
            "منخفض",
            "طبيعي"
        ]
    )

filtered = df[
    df["الصنف"] == item
].copy()

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

if stock_status == "نافد":

    filtered = filtered[
        filtered["المتبقي"] <= 0
    ]

elif stock_status == "منخفض":

    filtered = filtered[
        (filtered["المتبقي"] > 0)
        &
        (filtered["المتبقي"] < filtered["المنصرف"])
    ]

elif stock_status == "طبيعي":

    filtered = filtered[
        filtered["المتبقي"] >= filtered["المنصرف"]
    ]
st.divider()
# ----------------------------
# مؤشرات الصنف
# ----------------------------

total_begin = filtered["رصيد البداية"].sum()

total_in = filtered["الوارد"].sum()

total_out = filtered["المنصرف"].sum()

total_remaining = filtered["المتبقي"].sum()

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "رصيد البداية",
    f"{total_begin:,.0f}",
    border=True
)

c2.metric(
    "الوارد",
    f"{total_in:,.0f}",
    border=True
)

c3.metric(
    "المنصرف",
    f"{total_out:,.0f}",
    border=True
)

c4.metric(
    "المتبقي",
    f"{total_remaining:,.0f}",
    border=True
)

st.divider()

# ----------------------------
# الرصيد حسب المصدر
# ----------------------------

summary = (
    filtered
    .groupby("المصدر")["المتبقي"]
    .sum()
    .reset_index()
)

st.subheader("رصيد الصنف حسب المصدر")

st.dataframe(
    summary,
    use_container_width=True
)

fig = px.bar(
    summary,
    x="المصدر",
    y="المتبقي",
    title=f"رصيد {item}",
    text_auto=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()
# ----------------------------
# الرصيد حسب الفرع
# ----------------------------

branch_summary = (
    filtered
    .groupby("الفرع")["المتبقي"]
    .sum()
    .reset_index()
    .sort_values(
        "المتبقي",
        ascending=False
    )
)

st.subheader("رصيد الصنف بالفرع")

st.dataframe(
    branch_summary,
    use_container_width=True
)

fig2 = px.bar(
    branch_summary,
    x="الفرع",
    y="المتبقي",
    title=f"{item} حسب الفروع",
    text_auto=True
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.divider()
# ----------------------------
# التفاصيل
# ----------------------------

st.subheader("البيانات التفصيلية")

st.dataframe(
    filtered,
    use_container_width=True
)