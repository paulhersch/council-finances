from pandas import DataFrame, Series
from decimal import Decimal
from datetime import date

from finanztool.lib.tables.base import abstract_get, abstract_edit


def _format_belegid_num(rechnungsdatum: date, is_einnahme: bool, fortlaufend: int):
    return f"{'E' if is_einnahme else 'A'}{rechnungsdatum.strftime('%Y%m%d')}{str(fortlaufend).zfill(3)}"


def _next_belegid(df: DataFrame, is_einnahme: bool, datum: date):
    df.set_index("belegid", drop=False, inplace=True)

    # Andere Belege am gleichen Datum
    index = len(df.filter(like=datum.strftime("%Y%m%d"), axis=0)) + 1
    candidate = _format_belegid_num(datum, is_einnahme, index)
    done = False
    while not done:
        try:
            done = df.loc[candidate] is None
            index += 1
            candidate = _format_belegid_num(datum, is_einnahme, index)
        except KeyError:
            done = True

    df.reset_index(drop=True, inplace=True)
    return candidate


# damit DF Format immer eingehalten wird
def _new_df_row(
    posten,
    belegid,
    rechnungsdatum,
    transaktionsdatum,
    beschlussid,
    empfaenger,
    zweck,
    betrag,
    auf_konto,
    bemerkung,
):
    return Series(
        {
            "posten": posten,
            "belegid": belegid,
            "rechnungsdatum": rechnungsdatum,
            "transaktionsdatum": transaktionsdatum,
            "beschlussid": beschlussid,
            "empfaenger": empfaenger,
            "zweck": zweck,
            "betrag": betrag,
            "auf_konto": auf_konto,
            "bemerkung": bemerkung,
            # Zeilen dürfen nicht leer sein weil Pandas
            "stand_konto": Decimal(0),
            "stand_barkasse": Decimal(0),
            "stand_gesamt": Decimal(0),
        }
    )


def update_balances(df: DataFrame):
    konto = Decimal(0)
    kasse = Decimal(0)

    def _apply_fun(row):
        nonlocal konto, kasse
        is_einnahme = row.posten[0] == "E"

        if row.auf_konto:
            konto += row.betrag if is_einnahme else -row.betrag
        else:
            kasse += row.betrag if is_einnahme else -row.betrag
        row.stand_konto = konto
        row.stand_barkasse = kasse
        row.stand_gesamt = konto + kasse
        return row

    # apply ist wohl schneller als rohe Iteration (Antwort 2)
    # https://stackoverflow.com/questions/16476924
    new = df.apply(_apply_fun, axis=1, raw=False)
    return new


def add_transaction(
    df: DataFrame,
    posten: str,
    rechnungsdatum: date,
    transaktionsdatum: date,
    betrag: Decimal,
    zweck: str,
    empfaenger: str,
    nutze_konto: bool,
    beschlussid: str = None,
    bemerkung: str = "",
    full_update: bool = True,
) -> (DataFrame, str):
    """
    Fügt eine Transaktion zu transaktionen.csv zurück. Gibt Tupel
    der Form (df, belegid) zurück,
    wobei Belegid automatisch aus dem Kontext des DF ermittelt wird
    **Kann nur fortlaufend rechnen!**

    :param transactions_DF: akutelles Dataframe von `transaktionen.csv`
    :param posten: Der Posten aus dem Haushaltsplan, dem die Transaktion zugeteilt
      werden soll, Präfix A -> Ausgabe und Präfix E -> Einnahme
    :param rechnungsdatum: Datum auf der Rechnung
    :param beschlussid: ID des zugehörigen Beschlusses
    :param transaktionsdatum: Datum der Transaktion (z.B: Banküberweisung)
    :param betrag: Betrag der Transaktion (in Euro), z.B. 10.2 für 10,20€
    :param zweck: Der Zweck der Transaktion z.B. "Grillgut Erstigrillen"
    :param empfaenger: Empfänger der Transaktion
    :param nutze_konto: Ob Transaktion über das Konto abgelaufen ist
    :param bemerkung: Zusätzlicher Kommentar zu der Transaktion
    :param full_update: Ob die Kontostände direkt updated werden sollen. Default: True
    """
    is_einnahme: bool = str.__contains__(posten, "E")
    # default sollte bei übergeordneten Programmteilen gesetzt werden
    # empfaenger = "FSR Mathe/Info" if (is_einnahme and empfaenger is None) else empfaenger

    # Zu ermitteln
    belegid: str = None
    beschlussid: str = "noID" if beschlussid is None else beschlussid
    belegid = _next_belegid(df, is_einnahme, rechnungsdatum)

    new_row = _new_df_row(
        posten,
        belegid,
        rechnungsdatum,
        transaktionsdatum,
        beschlussid,
        empfaenger,
        zweck,
        betrag,
        nutze_konto,
        bemerkung,
    )

    # füge neu ein und sortiere nach t_datum
    df.loc[len(df)] = new_row
    df.sort_values(by=["transaktionsdatum", "betrag"], inplace=True, ignore_index=True)

    if full_update:
        df = update_balances(df)

    return (df, belegid)


def delete_transaction(
    df: DataFrame, belegid: str, full_update: bool = True
) -> DataFrame:
    """
    Löscht Transaktion mit gegebener BelegID
    Falls ID None oder "" ist, wird ein Fehler geworfen

    :param transactions_DF: Der DataFrame mit Transaktionen
    :param belegid: Die BelegID der ausgewählten Transaktion
    :param full_update: Ob ein Update der Kontostände durchgeführt werden soll (default: True, optional)
    """
    if belegid is None or belegid == "":
        raise KeyError()

    transactions_DF = (
        df.set_index("belegid").drop(index=belegid).reset_index(drop=False)
    )

    if full_update:
        transactions_DF = update_balances(transactions_DF)

    return transactions_DF


def edit_transaction(
    df: DataFrame,
    belegid: str,
    beschlussid_new: str | None = None,
    transaction_date_new: date | None = None,
) -> DataFrame:
    """
    Gibt Transaktion mit gegebener BelegID eine andere BeschlussID

    :param transactions_DF: Der DataFrame mit Transaktionen
    :param belegid: Die BelegID der ausgewählten Transaktion
    :param beschlussid: Die neue BeschlussID der Transaktion (optional)
    """
    return abstract_edit(
        df,
        belegid,
        "belegid",
        {"beschlussid": beschlussid_new, "transaktionsdatum": transaction_date_new},
    )


def get_transactions(
    df: DataFrame,
    posten: str,
    rechungsdatum: date,
    transaktionsdatum: date,
    beschlussid: str,
    empfaenger: str,
    zweck: str,
):
    filters = {
        "posten": posten,
        "rechnungsdatum": rechungsdatum,
        "transaktionsdatum": transaktionsdatum,
        "beschlussid": beschlussid,
        "empfaenger": empfaenger,
        "zweck": zweck,
    }

    return abstract_get(df, filters)
