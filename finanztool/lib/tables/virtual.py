from pandas import DataFrame, Series
from decimal import Decimal


"""
Generatoren für 'virtuelle' Tabellen (ähnlich der Art und
Weise wie virtual Tables in Postgres funktionieren)

Enthält Funktionen, welche Tabellen entsprechend der csv
Spezifikation ausgeben
"""


def gen_bilanz(
    base_df: DataFrame,
    data_df: DataFrame,
    keycol: str,
    data_col_base: str,
    data_col_data: str,
    is_einnahme: callable,
    col_name_real: str = 'real',
    col_name_diff: str = 'diff'
) -> DataFrame:
    """
    Generiere Bilanzspalten auf base_df. Beispiel: Bilanz über verwendete
    Gelder verschiedener Posten im Haushaltsplan.

     - falls für Daten aus data_df via keycol keine Zuordnung in base_df gefunden werden kann
       werden diese Daten ignoriert
     - falls die Spalten über data_col_data und data_col_base nicht die gleichen Typen haben und
       nicht automatisch in verrechenbare Typen umgewandelt werden können, wird der Fehler
       weitergegeben


    :param base_df: Der Ausgangsdataframe, in den Spalten eingefügt werden sollen
    :param data_df: Der Dataframe mit Daten, aus dem Daten ausgelesen werden
    :param keycol: Die Spalte, über welche Daten aus data_df den Zeilen in base_df zugeordnet werden
    :param data_col_data: Die Spalte in data_df, welche gesuchte Daten enthält
    :param data_col_base: Die Spalte in base_df, welche Basisdaten enthält
    :param is_einnahme: Funktion, welche mit Schlüssel aus keycol aussagt, ob Einnahme vorliegt
    :param col_name_real: Spaltenname für reine Daten in Ausgabe-DF für Spalte
    :param col_name_diff: Spaltenname für Verknüpfung der Daten (z.B. base.daten - data.daten bei Ausgaben)
    """
    data_by_baseid = {
        base_df.loc[i][keycol]: Decimal(0) for i in range(len(base_df))
    }

    def fill_data_dict(row: Series):
        nonlocal data_by_baseid
        row_index = row[keycol]
        # schreibe nur Daten, für die ein Index in base_df existiert
        if row_index in data_by_baseid.keys():
            data_by_baseid[row_index] += row[data_col_data]
        return row

    data_df.apply(fill_data_dict, axis=1)

    return base_df.assign(**{
        col_name_real: [
            data_by_baseid[base_df.loc[i][keycol]]
            for i in range(len(base_df))
        ],
        col_name_diff: [
            (
                (
                    data_by_baseid[base_df.loc[i][keycol]] - base_df.loc[i][data_col_base]
                ) if is_einnahme(base_df.loc[i][keycol]) else (
                    base_df.loc[i][data_col_base] - data_by_baseid[base_df.loc[i][keycol]]
                )
            )
            for i in range(len(base_df))
        ]
    })


def plan_bilanz(
    haushaltsplan: DataFrame,
    transaktionen: DataFrame
) -> DataFrame:
    return gen_bilanz(
        base_df=haushaltsplan,
        data_df=transaktionen,
        keycol='posten',
        data_col_base='betrag',
        data_col_data='betrag',
        is_einnahme=lambda s: s[0] == "E"
    )


def beschluesse_bilanz(
    beschluesse: DataFrame,
    transaktionen: DataFrame
):

    beschluesse_id_index = beschluesse.set_index('beschlussid')
    return gen_bilanz(
        base_df=beschluesse,
        data_df=transaktionen,
        keycol='beschlussid',
        data_col_data='betrag',
        data_col_base='betrag',
        is_einnahme=lambda s: beschluesse_id_index.loc[s]['posten'][0] == "E",
        col_name_real='ausgegeben',
        col_name_diff='übrig'
    )
