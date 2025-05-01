"""
Oneshot Aufruf von status
"""
from finanztool.lib.files import Tables
from finanztool.lib.tables.virtual import gen_bilanz, beschluesse_bilanz, plan_bilanz
from pandas import Series
from decimal import Decimal


def status(
    tables: Tables,
    args
):
    """
    :param tables: Tables Objekt des ausgewählten Jahres
    :param args: Rückgabe des argparsers
    """
    match args.status_type:
        case "transactions":
            tables.pprint('transaktionen')

        case "transactions_konto":
            tables.pprint(
                tables.transaktionen[[
                    'posten',
                    'betrag',
                    'auf_konto',
                    'belegid',
                    'transaktionsdatum',
                    'zweck',
                    'empfaenger',
                    'beschlussid',
                    'stand_konto',
                    'stand_barkasse'
                ]]
                .set_index('auf_konto', drop=True)
                .loc[True]
            )

        case "resolutions":
            tables.pprint(
                beschluesse_bilanz(
                    beschluesse=tables.beschluesse,
                    transaktionen=tables.transaktionen
                )
            )

        case "plan":
            tables.pprint(
                plan_bilanz(
                    haushaltsplan=tables.haushaltsplan,
                    transaktionen=tables.transaktionen
                )
            )

        case "posten":
            trans_posten_df = tables.transaktionen.set_index('posten').filter(like=args.posten, axis=0)
            beschl_posten_df = tables.beschluesse.set_index('posten').filter(like=args.posten, axis=0)
            plan_posten = tables.haushaltsplan.set_index('posten')
            soll = plan_posten.loc[args.posten].betrag
            geplant = sum([b.betrag for b in beschl_posten_df.itertuples()])
            ist = sum([t.betrag for t in trans_posten_df.itertuples()])
            # Zeige bisherige Transaktionen unter Posten als Tabelle
            print(f"\033[1mTransaktionen auf Posten \"{plan_posten.loc[args.posten].titel}\":\033[0m")
            if trans_posten_df.shape[0] == 0:
                print("-")
            else:
                tables.pprint(trans_posten_df[["belegid", "transaktionsdatum", "zweck", "empfaenger", "betrag"]])

                print("\n\033[1mBeschlüsse zu Posten:\033[0m")
            if beschl_posten_df.shape[0] == 0:
                print("-")
            else:
                tables.pprint(beschl_posten_df)

            # Verändere Aussage abhängig von Einnahme oder Ausgabe
            is_einnahme = args.posten[0] == "E"
            if is_einnahme:
                print(f"Beschlossene Einnahmen: {geplant}€")
            else:
                print(f"Beschlossene Ausgaben: {geplant}€")
            print(f"\nGeplante {'Einnahmen' if is_einnahme else 'Ausgaben'}: {soll}€")
            print(f"Bisher {'erhalten' if is_einnahme else 'ausgegeben'}: {ist}€")
            if soll <= ist:
                if is_einnahme:
                    print(f"\033[1;32mEinnahmenüberschuss auf Posten {args.posten}: {ist-soll}€\033[0m")
                else:
                    print(f"\033[1;31mAktuelles Minus: {soll - ist}€\033[0m")
            else:
                if is_einnahme:
                    print(f"\033[1;31mNoch nicht erhaltene Einnahmen für {args.posten}: {-(ist-soll)}€")
                else:
                    print(f"\033[1;32mÜbriges Budget (nach Posten): {soll-ist}€")

        case "noid":
            tables.pprint(
                tables.transaktionen
                .set_index('beschlussid')
                .filter(like='noID', axis=0)
                .reset_index()
                # Einnahmen brauchen keine Beschlussid -> Filtere nur nach Ausgaben
                .set_index('posten')
                .filter(like='A', axis=0)
                .reset_index()
            )
