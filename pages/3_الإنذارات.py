import streamlit as st
import plotly.express as px
st.set_page_config(
    page_title="Alarm",
    page_icon="🚨 Annotation 2026-03-11 213816.png",
    layout="wide"
)

from auth import check_login, show_logo

check_login()
show_logo()
import streamlit as st
import pandas as pd

from utils.data_loader import load_data

st.set_page_config(layout="wide")

col1, col2 = st.columns([1,5])
with col1:
    st.image(
        "Annotation 2026-03-11 213816.png",
        width=50
    )

with col2:
    st.title("🚨 Alarm  ")



st.divider()

df = load_data()

# ======================
# تنظيف الأرقام
# ======================

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

# ======================
# Sidebar Filters
# ======================

st.subheader("⚙️ الفلاتر")

c1,c2,c3 = st.columns(3)

with c1:
    years = sorted(df["السنة"].dropna().unique())
    year_filter = st.multiselect(
        "السنة",
        years,
        default=years
    )

with c2:
    months = sorted(df["الشهر"].dropna().unique())
    month_filter = st.multiselect(
        "الشهر",
        months,
        default=months
    )

with c3:
    sources = sorted(df["المصدر"].dropna().unique())
    source_filter = st.multiselect(
        "المصدر",
        sources,
        default=sources
    )

c4,c5 = st.columns(2)

with c4:
    branches = sorted(df["الفرع"].dropna().unique())
    branch_filter = st.multiselect(
        "الفرع",
        branches,
        default=branches
    )

with c5:
    items = sorted(df["الصنف"].dropna().unique())
    item_filter = st.multiselect(
        "الصنف",
        items
    )

st.divider()

# ======================
# تطبيق الفلاتر
# ======================

filtered = df[
    df["السنة"].isin(year_filter)
]

filtered = filtered[
    filtered["الشهر"].isin(month_filter)
]

filtered = filtered[
    filtered["المصدر"].isin(source_filter)
]

filtered = filtered[
    filtered["الفرع"].isin(branch_filter)
]

if item_filter:
    filtered = filtered[
        filtered["الصنف"].isin(item_filter)
    ]

# ======================
# KPI
# ======================

zero_stock = filtered[
    filtered["المتبقي"] <= 0
]

LOW_STOCK_LIMIT = 50

low_stock = filtered[
    (filtered["المتبقي"] > 0)
    &
    (filtered["المتبقي"] <= LOW_STOCK_LIMIT)
]
c1,c2,c3 = st.columns(3)

c1.metric(
    "🔴 نافد",
    len(zero_stock)
)

c2.metric(
    "🟡 منخفض",
    len(low_stock)
)

c3.metric(
    "📦 إجمالي السجلات",
    len(filtered)
)

st.divider()

# ======================
# أصناف نافدة
# ======================

st.subheader("🔴 أصناف نافدة")

st.dataframe(
    zero_stock[
        [
            "الفرع",
            "الصنف",
            "المتبقي",
            "المصدر",
            "الشهر",
            "السنة"
        ]
    ],
    use_container_width=True
)


st.divider()
# ======================
# أصناف منخفضة
# ======================

st.subheader("🟡 أصناف منخفضة")

st.dataframe(
    low_stock[
        [
            "الفرع",
            "الصنف",
            "المنصرف",
            "المتبقي",
            "المصدر",
            "الشهر",
            "السنة"
        ]
    ],
    use_container_width=True
)


st.divider()
# ======================
# أعلى استهلاك
# ======================

st.subheader("🔥 أعلى الأصناف استهلاكاً")

top_items = (
    filtered
    .groupby("الصنف")["المنصرف"]
    .sum()
    .reset_index()
    .sort_values(
        "المنصرف",
        ascending=False
    )
    .head(20)
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

st.dataframe(
    top_items,
    use_container_width=True
)

