"""
oneshot Aufrufe von transactions als subcommand
"""

from finanztool.lib.files import Tables
from finanztool.lib.tables.transactions import (
    add_transaction,
    edit_transaction,
    get_transactions,
    delete_transaction,
    update_balances,
)


def transactions(tables: Tables, args):
    """
    :param tables: Tables Objekt des ausgewählten Jahres
    :param args: Rückgabe des argparsers
    """
    match args.transactions_action:
        case "add":
            tables.transaktionen, b_id = add_transaction(
                tables.transaktionen,
                args.posten,
                args.rechnungsdatum,
                args.transaktionsdatum,
                args.betrag,
                args.zweck,
                args.empfaenger,
                args.nutze_konto,
                beschlussid=args.beschlussid,
                bemerkung=args.comment,
            )
            print(f"Transaktion mit Belegid {b_id} hinzugefügt")
            tables.save("transaktionen")

        case "delete":
            tables.transaktionen = delete_transaction(
                tables.transaktionen, args.belegid
            )
            print(f"Transaktion mit BelegID {args.belegid} gelöscht")
            tables.save("transaktionen")

        case "edit":
            tables.transaktionen = edit_transaction(
                tables.transaktionen,
                args.belegid,
                args.beschlussid,
                args.transaktionsdatum,
            )
            print(f"Transaktion mit BelegID {args.belegid} hat Änderungen erhalten:")
            print(
                f" -  BeschlussID: {args.beschlussid if args.beschlussid is not None else 'ungeändert'}"
            )
            print(
                f" -  Transaktionsdatum: {args.transaktionsdatum if args.transaktionsdatum is not None else 'ungeändert'}"
            )
            tables.save("transaktionen")
        case "get":
            tables.pprint(
                get_transactions(
                    tables.transaktionen,
                    args.posten,
                    args.rechnungsdatum,
                    args.transaktionsdatum,
                    args.beschlussid,
                    args.empfaenger,
                    args.zweck,
                )
            )
        case "recalc":
            tables.transaktionen = update_balances(tables.transaktionen)
            tables.transaktionen = tables.transaktionen.sort_values(
                ["transaktionsdatum", "betrag"], axis=0
            )
            tables.save("transaktionen")
