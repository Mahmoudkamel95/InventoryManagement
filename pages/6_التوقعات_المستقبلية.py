from auth import check_login, show_logo

check_login()
show_logo()

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.forecast import forecast_item, forecast_bulk

st.set_page_config(
    page_title="التوقعات المستقبلية",
    layout="wide"
)

st.title("🔮 توقع الاستهلاك والاحتياج")

MONTH_ORDER = {
    "يناير": 1, "فبراير": 2, "مارس": 3, "أبريل": 4,
    "مايو": 5, "يونيو": 6, "يوليو": 7, "أغسطس": 8,
    "سبتمبر": 9, "أكتوبر": 10, "نوفمبر": 11, "ديسمبر": 12
}

df = load_data()

# تنظيف الأعمدة الرقمية
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

# تنظيف أعمدة النص من المسافات الزايدة
for col in ["الفرع", "الصنف", "الشهر", "المصدر"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

has_source_col = "المصدر" in df.columns

# -------------------
# وضع التحليل
# -------------------

mode = st.radio(
    "وضع التحليل",
    [
        "فرع وصنف محدد",
        "كل الأصناف في فرع واحد",
        "كل الفروع لصنف واحد",
        "تقرير شامل (كل الفروع وكل الأصناف)"
    ],
    horizontal=True
)

# -------------------
# فلتر نوع المصدر (مخزن / سيارة / إقليم)
# -------------------

source_choice = None        # يُستخدم في وضع "فرع وصنف محدد" فقط
sources_for_bulk = None     # يُستخدم في باقي الأوضاع (تحليل دفعة)
scoped_df = df

if has_source_col:
    source_types = sorted(df["المصدر"].dropna().unique())

    if mode == "فرع وصنف محدد":
        source_choice = st.selectbox(
            "نوع المصدر",
            source_types
        )
        scoped_df = df[df["المصدر"] == source_choice]

    else:
        picked_sources = st.multiselect(
            "نوع المصدر (سيبها فاضية = كل الأنواع: مخازن وسيارات وأقاليم)",
            source_types
        )
        sources_for_bulk = picked_sources if picked_sources else None
        scoped_df = (
            df[df["المصدر"].isin(picked_sources)]
            if picked_sources
            else df
        )

# -------------------
# الفلاتر
# -------------------

f1, f2, f3 = st.columns(3)

branch = None
item = None

if mode in ["فرع وصنف محدد", "كل الأصناف في فرع واحد"]:
    with f1:
        branch = st.selectbox(
            "الفرع",
            sorted(scoped_df["الفرع"].dropna().unique())
        )

if mode in ["فرع وصنف محدد", "كل الفروع لصنف واحد"]:
    with f2:
        item = st.selectbox(
            "الصنف",
            sorted(scoped_df["الصنف"].dropna().unique())
        )

years = sorted(
    pd.to_numeric(df["السنة"], errors="coerce").dropna().unique()
)

with f3:
    year_choice = st.selectbox(
        "السنة",
        ["كل السنوات"] + [str(int(y)) for y in years]
    )

year = None if year_choice == "كل السنوات" else year_choice

status_filter = st.multiselect(
    "حالة المخزون (لفلترة النتائج)",
    [
        "🔴 خطر شديد",
        "🟠 خطر",
        "🟡 يحتاج متابعة",
        "🟢 آمن",
        "🔵 راكد"
    ],
    default=[
        "🔴 خطر شديد",
        "🟠 خطر",
        "🟡 يحتاج متابعة",
        "🟢 آمن",
        "🔵 راكد"
    ]
)

# -------------------

if st.button("🚀 تشغيل التحليل"):

    if mode == "فرع وصنف محدد":
        result = forecast_item(df, item, branch, source=source_choice)

        if not result.empty:
            result.insert(0, "الفرع", branch)
            if has_source_col:
                result.insert(0, "المصدر", source_choice)

    elif mode == "كل الأصناف في فرع واحد":
        result = forecast_bulk(
            df, branches=[branch], items=None,
            sources=sources_for_bulk, year=year
        )

    elif mode == "كل الفروع لصنف واحد":
        result = forecast_bulk(
            df, branches=None, items=[item],
            sources=sources_for_bulk, year=year
        )

    else:
        result = forecast_bulk(
            df, branches=None, items=None,
            sources=sources_for_bulk, year=year
        )

    if result.empty:
        st.error("لا توجد بيانات كافية")

    else:
        result = result[result["الحالة"].isin(status_filter)]

        if result.empty:
            st.warning("لا توجد نتائج مطابقة لفلتر الحالة المختار")

        elif mode == "فرع وصنف محدد" and len(result) == 1:

            r = result.iloc[0]

            if has_source_col:
                st.caption(f"📍 نوع المصدر: {source_choice}")

            k1, k2, k3, k4 = st.columns(4)

            k1.metric("متوسط آخر 3 شهور", r["متوسط_آخر_3_شهور"])
            k2.metric("المخزون الحالي", int(r["المخزون_الحالي"]))
            k3.metric("أشهر التغطية", r["أشهر_التغطية"])
            k4.metric("الطلب المقترح", int(r["كمية_الطلب_المقترحة"]))

            st.divider()
            st.subheader("🚨 تقييم المخزون")

            if r["الحالة"] == "🔴 خطر شديد":
                st.error(r["الحالة"])
            elif r["الحالة"] == "🟠 خطر":
                st.error(r["الحالة"])
            elif "يحتاج" in r["الحالة"]:
                st.warning(r["الحالة"])
            elif r["الحالة"] == "🔵 راكد":
                st.info(r["الحالة"])
            else:
                st.success(r["الحالة"])

            st.divider()
            st.subheader("📋 تفاصيل التوقع")
            st.dataframe(result, use_container_width=True)

            history = df[
                (df["الفرع"] == branch) & (df["الصنف"] == item)
            ].copy()

            if has_source_col:
                history = history[history["المصدر"] == source_choice]

            history["month_num"] = history["الشهر"].map(MONTH_ORDER)

            history["السنة"] = pd.to_numeric(
                history["السنة"],
                errors="coerce"
            )

            history = history.dropna(
                subset=["month_num", "السنة"]
            )

            # لو المستخدم اختار سنة معينة
            if year is not None:

                history = history[
                    history["السنة"] ==
                    pd.to_numeric(year)
                ]

            history = history.sort_values(
                ["السنة", "month_num"]
            )

            # اسم يظهر على المحور بالشكل:
            # يناير 2026
            # فبراير 2026
            history["الفترة"] = (
                history["الشهر"]
                + " "
                + history["السنة"].astype(int).astype(str)
            )

            st.subheader("📈 الاستهلاك التاريخي")

            fig = px.line(
                history,
                x="الفترة",
                y="المنصرف",
                markers=True,
                title="الاستهلاك الشهري"
            )

            fig.update_layout(
                xaxis_title="الشهر",
                yaxis_title="الكمية المنصرفة",
                height=500
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
        else:
            st.subheader("📊 ملخص الحالة")

            s1, s2, s3 = st.columns(3)

            s1.metric("🔴 خطر شديد", int((result["الحالة"] == "🔴 خطر شديد").sum()))
            s2.metric("🟡 يحتاج متابعة", int((result["الحالة"] == "🟡 يحتاج متابعة").sum()))
            s3.metric("🟢 آمن", int((result["الحالة"] == "🟢 آمن").sum()))

            if has_source_col and "المصدر" in result.columns:
                st.divider()
                st.subheader("📦 توزيع الاحتياج حسب نوع المصدر")

                source_summary = (
                    result.groupby("المصدر")["الحالة"]
                    .apply(lambda s: (s == "🔴 خطر شديد").sum())
                    .reset_index(name="عدد حالات الخطر الشديد")
                )

                st.dataframe(source_summary, use_container_width=True)

            st.divider()
            st.subheader("📋 تفاصيل التوقع لكل الأصناف/الفروع")

            result = result.sort_values(
                "أشهر_التغطية",
                na_position="last"
            )

            display_result = result.copy()

            display_result["أشهر_التغطية"] = (
                display_result["أشهر_التغطية"]
                .fillna("لا يوجد استهلاك")
            )

            st.dataframe(
                display_result,
                use_container_width=True
            )
            st.divider()