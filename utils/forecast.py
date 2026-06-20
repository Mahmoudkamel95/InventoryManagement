import pandas as pd
import numpy as np


def forecast_item(df, item, branch=None, source=None):

    data = df.copy()

    # تنظيف الأعمدة الرقمية
    for col in [
        "رصيد البداية",
        "الوارد",
        "المنصرف",
        "المتبقي"
    ]:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        ).fillna(0)

    # تنظيف أعمدة النص من المسافات الزايدة
    # (السبب الأساسي اللي كان بيخرب الترتيب الزمني)
    for col in ["الفرع", "الصنف", "الشهر", "المصدر"]:
        if col in data.columns:
            data[col] = data[col].astype(str).str.strip()

    # فلترة الصنف
    data = data[
        data["الصنف"] == str(item).strip()
    ]

    if branch:
        data = data[
            data["الفرع"] == str(branch).strip()
        ]

    # فلترة نوع المصدر (مخزن / سيارة / إقليم) لو العمود موجود ومحدد
    if source and "المصدر" in data.columns:
        data = data[
            data["المصدر"] == str(source).strip()
        ]

    if len(data) == 0:
        return pd.DataFrame()

    # ترتيب زمني
    month_order = {
        "يناير": 1,
        "فبراير": 2,
        "مارس": 3,
        "أبريل": 4,
        "مايو": 5,
        "يونيو": 6,
        "يوليو": 7,
        "أغسطس": 8,
        "سبتمبر": 9,
        "أكتوبر": 10,
        "نوفمبر": 11,
        "ديسمبر": 12
    }

    data["month_num"] = data["الشهر"].map(month_order)

    # تحويل السنة لرقم صحيح عشان الترتيب يكون مضبوط
    data["السنة"] = pd.to_numeric(
        data["السنة"],
        errors="coerce"
    )

    # *** التعديل الأساسي ***
    # أي صف فيه اسم شهر غير معروف أو سنة فاضية (خطأ كتابي/صف فاضي)
    # لازم يتشال قبل الترتيب، لأن pandas بيرمي قيم NaN في آخر
    # الترتيب الافتراضي، فكان بيخلي صف غلط يظهر كـ "آخر شهر"
    # بدل الشهر الحقيقي اللي فيه الرصيد الصحيح.
    before_drop = len(data)
    data = data.dropna(subset=["month_num", "السنة"])
    dropped = before_drop - len(data)

    if len(data) == 0:
        return pd.DataFrame()

    # حماية إضافية: لو فيه صفين بنفس الشهر ونفس السنة لنفس
    # الفرع/الصنف (تكرار حقيقي، أو صف تمبليت لشهر مستقبلي
    # لسه فاضي بنفس الاسم)، نفضّل الصف اللي قيمة "المتبقي"
    # فيه أكبر (الصف الحقيقي) على الصف الفاضي بصفر.
    data = data.sort_values(
        ["السنة", "month_num", "المتبقي"]
    ).drop_duplicates(
        subset=["السنة", "month_num"],
        keep="last"
    ).reset_index(drop=True)

    # متوسط آخر 3 شهور
    last3 = data.tail(3)
    avg3 = last3["المنصرف"].mean()

    # متوسط آخر 6 شهور
    last6 = data.tail(6)
    avg6 = last6["المنصرف"].mean()

    # المخزون الحالي = المتبقي في آخر شهر فعلي بعد الترتيب الصحيح
    current_stock = data.iloc[-1]["المتبقي"]

    # أشهر التغطية
    # أشهر التغطية

    if avg3 > 0:

        coverage = round(
            current_stock / avg3,
            1
        )

    else:

        coverage = np.nan


    # كمية الطلب المقترحة

    target_stock = (avg3 * 6) + (avg3 * 0.25)

    reorder_qty = max(
        target_stock - current_stock,
        0
    )


    # حالة المخزون

    if avg3 == 0:

        status = "🔵 راكد"

    elif coverage < 1:

        status = "🔴 خطر شديد"

    elif coverage < 3:

        status = "🟠 خطر"

    elif coverage < 6:

        status = "🟡 يحتاج متابعة"

    else:

        status = "🟢 آمن"

    result = pd.DataFrame({

        "الصنف": [item],

        "متوسط_آخر_3_شهور": [
            round(avg3, 1)
        ],

        "متوسط_آخر_6_شهور": [
            round(avg6, 1)
        ],

        "المخزون_الحالي": [
            current_stock
        ],

        "أشهر_التغطية": [
            coverage
        ],

        "كمية_الطلب_المقترحة": [
            int(reorder_qty)
        ],

        "الحالة": [
            status
        ]
    })

    # ملاحظة تشخيصية: لو حابب تتأكد إن فيه صفوف اتشالت
    # ممكن تشيل التعليق عن السطر ده وتشوف كام صف كان فيه مشكلة
    # print(f"تم استبعاد {dropped} صف بسبب خطأ في الشهر/السنة")

    return result


def forecast_bulk(df, branches=None, items=None, sources=None, year=None):
    """
    تشغيل forecast_item على كل التوافيق المطلوبة من فرع/صنف/مصدر
    وترجيع جدول واحد فيه كل النتائج مرة واحدة.

    branches: قايمة فروع محددة، أو None يعني كل الفروع الموجودة
    items: قايمة أصناف محددة، أو None يعني كل الأصناف الموجودة
    sources: قايمة أنواع مصدر محددة (مخزن/سيارة/إقليم)، أو None يعني
             كل الأنواع الموجودة (هيتعمل لكل نوع تنبؤ مستقل، مش هيتم
             دمجهم في رقم واحد، عشان مخزون مخزن غير مخزون سيارة)
    year: سنة معينة لتقييد البيانات المستخدمة في الحساب، أو None لكل السنوات
    """

    data = df.copy()

    has_source_col = "المصدر" in data.columns

    for col in ["الفرع", "الصنف", "المصدر"]:
        if col in data.columns:
            data[col] = data[col].astype(str).str.strip()

    if year:
        data["السنة"] = pd.to_numeric(
            data["السنة"],
            errors="coerce"
        )
        data = data[
            data["السنة"] == pd.to_numeric(year, errors="coerce")
        ]

    if len(data) == 0:
        return pd.DataFrame()

    branch_list = (
        [str(b).strip() for b in branches]
        if branches
        else sorted(data["الفرع"].dropna().unique())
    )

    item_list = (
        [str(i).strip() for i in items]
        if items
        else sorted(data["الصنف"].dropna().unique())
    )

    if has_source_col:
        source_list = (
            [str(s).strip() for s in sources]
            if sources
            else sorted(data["المصدر"].dropna().unique())
        )
    else:
        # لو عمود المصدر غير موجود في الداتا، بنشغل التحليل عادي بدونه
        source_list = [None]

    rows = []

    for b in branch_list:
        for it in item_list:
            for s in source_list:
                res = forecast_item(data, it, b, source=s)
                if not res.empty:
                    if has_source_col:
                        res.insert(0, "المصدر", s)
                    res.insert(0, "الفرع", b)
                    rows.append(res)

    if not rows:
        return pd.DataFrame()

    return pd.concat(rows, ignore_index=True)