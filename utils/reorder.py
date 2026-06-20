def reorder_engine(df):
    
    result = df.copy()

    # مخزون الأمان 25%
    result["مخزون_الأمان"] = (
        result["المنصرف"] * 0.25
    )

    # الاحتياج المتوقع 3 أشهر
    result["الاحتياج_المتوقع"] = (
        result["المنصرف"] * 3
    )

    # كمية الطلب المقترحة
    result["كمية_الطلب_المقترحة"] = (

        result["الاحتياج_المتوقع"]

        +

        result["مخزون_الأمان"]

        -

        result["المتبقي"]

    )

    result["كمية_الطلب_المقترحة"] = (
        result["كمية_الطلب_المقترحة"]
        .clip(lower=0)
        .round()
        .astype(int)
    )

    # أيام التغطية

    result["أيام_التغطية"] = (
        result["المتبقي"]
        /
        (result["المنصرف"] / 30)
    )

    result["أيام_التغطية"] = (
        result["أيام_التغطية"]
        .replace([float("inf")], 999)
        .fillna(999)
        .round()
        .astype(int)
    )

    return result