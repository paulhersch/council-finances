from pandas import DataFrame, Series
from datetime import date
from decimal import Decimal

from finanztool.lib.tables.base import abstract_get, abstract_edit


def _next_beschlid(
    df: DataFrame,
    datum: date
):
    df.set_index('beschlussid', inplace=True, drop=False)

    index = len(df.filter(like=datum.strftime('%Y%m%d'), axis=0)) + 1
    candidate = f"B{datum.strftime('%Y%m%d')}{str(index).zfill(3)}"
    # finde alternative ID falls schon vergeben
    # no idea how this works™️
    done = False
    while not done:
        try:
            done = df.loc[candidate] is None
            index += 1
            candidate = f"B{datum.strftime('%Y%m%d')}{str(index).zfill(3)}"
        except KeyError:
            done = True

    df.reset_index(drop=True, inplace=True)
    return candidate


def _new_res_row(
    datum: date,
    posten: str,
    betrag: Decimal,
    beschlussid: str,
    zweck: str
):
    return Series({
        "datum": datum,
        "posten": posten,
        "betrag": betrag,
        "beschlussid": beschlussid,
        "zweck": zweck
    })


def add_resolution(
    df: DataFrame,
    datum: date,
    posten: str,
    betrag: Decimal,
    zweck: str,
) -> DataFrame:
    """
    Füge Beschluss hinzu

    :param df: Der DataFrame mit Beschlüssen
    :param datum: Das Datum des neuen Beschlusses
    :param posten: Der Posten, auf dem Beschluss abgerechnet wird
    :param zweck: Zweck des Postens
    """
    id = _next_beschlid(df, datum)
    new_row = _new_res_row(datum, posten, betrag, id, zweck)

    df.loc[len(df)] = new_row
    df.sort_values(by=['beschlussid'], inplace=True)

    return df, id


def edit_resolution(
    df: DataFrame,
    beschlussid: str,
    betrag: Decimal,
    posten: str
) -> DataFrame:
    """
    Bearbeite den via BeschlussID spezifizierten Beschluss

    :param df: der DataFrame mit Beschlüssen
    :param beschlussid: Die BeschlussID
    :param betrag: Der neue Betrag des Beschlusses
    :param posten: Der neue Posten des Beschlusses
    """
    return abstract_edit(
        df,
        beschlussid,
        'beschlussid',
        {
            'betrag': betrag,
            'posten': posten
        }
    )


def get_resolutions(
    df: DataFrame,
    posten: str,
    datum: date,
    zweck: str
) -> DataFrame:
    """
    Filtere Beschlüsse über Posten und Datum.

    :param df: der DataFrame mt Beschlüssen
    :param posten: Der Posten des Beschlusses
    :param datum: Datum des Beschlusses
    :param zweck: Teilstring des Beschlusszwecks
    """
    filters = {
        'posten': posten,
        'datum': datum,
        'zweck': zweck
    }

    return abstract_get(df, filters)


def delete_resolution(
    df: DataFrame,
    beschlussid: str
) -> DataFrame:
    """
    Lösche einen Beschluss.

    :param df: Der DataFrame mit Beschlüssen
    :param beschlussid: die ID des Beschlusses
    """
    df.set_index('beschlussid', drop=False, inplace=True)
    df.drop(index=beschlussid, inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df
