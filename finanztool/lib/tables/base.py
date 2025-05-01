from pandas import DataFrame


def abstract_get(df: DataFrame, filters: dict):
    """
    Expected Input: Dictionary mit folgender Form
    {
        Spaltenname: Wert
    }

    Falls `Wert` None ist, wird nicht nach dieser Spalte
    gefiltert.
    """
    for f_name in filters.keys():
        if filters[f_name] is not None:
            df.set_index(f_name, drop=False, inplace=True)
            df = df.filter(like=filters[f_name], axis=0)
            df.reset_index(inplace=True, drop=True)

    return df


def abstract_edit(df: DataFrame, primary, primary_column: str, filters: dict):
    """
    Expected Input: Dict mit folgender Form
    {
        spaltenname: Wert
    }
    Falls Wert für spaltenname None ist, wird der Wert in der Tabelle nicht
    überschrieben.

    `primary_column` dient zur Identifikation der Spalte des Primärschlüssels
    und primary ist der Wert der Index des Eintrags
    """
    df.set_index(primary_column, inplace=True, drop=True)
    if primary not in df.index:
        print(f"Primärschlüssel {primary} existiert nicht!!")
        exit(1)

    for k, v in filters.items():
        if v is not None:
            df.loc[primary, k] = v

    df.reset_index(drop=False, inplace=True)
    return df
