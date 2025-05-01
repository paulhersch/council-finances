from pathlib import Path
from argparse import ArgumentParser
from datetime import date, datetime
from decimal import Decimal


def get_current_year_folder() -> str:
    yeafile = Path(".year")
    if yeafile.exists():
        return yeafile.open("r").readline()
    directories = [
        d.name for d in Path(".").iterdir() if d.is_dir() and d.name.isnumeric()
    ]
    directories.sort(reverse=True)
    return directories[0] if len(directories) > 0 else datetime.now().strftime("%Y")


def date_parser(s) -> date:
    if s is None:
        return None
    return datetime.strptime(s, "%d-%m-%Y").date()


def concat_strlist(strlist):
    return " ".join(strlist)


def print_error(text: str) -> None:
    print(f"\033[1;31m{text}\033[0m")


def parse_args(argstr: str | None = None) -> dict:
    # Verpacken in Unterfunktionen für leichtere Verständlichkeit des eigentlichen
    # Codes. Sind sehr viele Unteroptionen
    def create_transaction_add_options(subparser: ArgumentParser):
        subparser.add_argument(
            "-p", dest="posten", help="Posten im Haushaltsplan", type=str
        )
        subparser.add_argument(
            "-r",
            dest="rechnungsdatum",
            help="Rechnungsdatum, Format (dd-mm-YYYY)",
            type=date_parser,
        )
        subparser.add_argument(
            "-t",
            dest="transaktionsdatum",
            help="Transaktionsdatum, Format (dd-mm-YYYY)",
            type=date_parser,
        )
        subparser.add_argument(
            "-i",
            dest="beschlussid",
            help="BeschlussID des zugehörigen Beschlusses",
            type=str,
        )
        subparser.add_argument(
            "-e", dest="empfaenger", help="Empfänger der Transaktion", nargs="+"
        )
        subparser.add_argument("-z", dest="zweck", help="Verwendungszweck", nargs="+")
        subparser.add_argument(
            "-b", dest="betrag", help="Betrag der Transaktion", type=Decimal
        )
        subparser.add_argument(
            "-c",
            dest="comment",
            help="Kommentar zur Transaktion",
            nargs="+",
            default=[""],
        )
        subparser.add_argument(
            "-k",
            dest="nutze_konto",
            action="store_true",
            help="Ob Transaktion auf Bankkonto gebucht werden soll (default: bar)",
        )

    def create_transactions_edit_options(subparser: ArgumentParser):
        subparser.add_argument("belegid", help="BelegID der zu ändernden Transaktion")
        subparser.add_argument(
            "-i", "--beschlussid", help="Die neue BeschlussID der Transaktion"
        )
        subparser.add_argument(
            "-t",
            "--transaktionsdatum",
            help="Das neue Transaktionsdatum, Format (dd-mm-YYYY)",
            type=date_parser,
        )

    def create_transactions_delete_options(subparser: ArgumentParser):
        subparser.add_argument(
            "belegid", help="Die BelegID der zu löschenden Transaktion"
        )

    def create_transactions_get_options(subparser: ArgumentParser):
        subparser.add_argument(
            "-p",
            "--posten",
        )
        subparser.add_argument("-r", "--rechnungsdatum")
        subparser.add_argument("-t", "--transaktionsdatum")
        subparser.add_argument("-i", "--beschlussid")
        subparser.add_argument("-e", "--empfaenger")
        subparser.add_argument("-z", "--zweck")

    def create_transactions_main(subparser: ArgumentParser):
        new_subparser_func = subparser.add_subparsers(dest="transactions_action")
        # interactive subcommand, durch transactins_action erkannt
        transactions_interactive = new_subparser_func.add_parser(
            "interactive",
            help="starte den Interaktiven Modus",
        )
        # add subcommand
        transactions_add = new_subparser_func.add_parser(
            "add", help="Füge einzelne Transaktion in Speicher ein (oneshot)"
        )
        create_transaction_add_options(transactions_add)
        # edit subcommand
        transactions_edit = new_subparser_func.add_parser(
            "edit", help="bearbeite Transaktionen"
        )
        create_transactions_edit_options(transactions_edit)
        # delete subcommand
        transactions_delete = new_subparser_func.add_parser(
            "delete", help="Lösche eine Transaktion"
        )
        create_transactions_delete_options(transactions_delete)
        # get subcommand
        transactions_get = new_subparser_func.add_parser(
            "get", help="Suche nach Transaktionen"
        )
        create_transactions_get_options(transactions_get)

        new_subparser_func.add_parser("recalc", help="Rekalkuliere Kassenstände")

        return (
            transactions_add,
            transactions_edit,
            transactions_delete,
            transactions_get,
            transactions_interactive,
        )

    def create_resolutions_add_options(subparser: ArgumentParser):
        subparser.add_argument("-d", "--datum", type=date_parser, help="Beschlussdatum")

        subparser.add_argument(
            "-p",
            "--posten",
            type=str,
            help="ID des Postens, zu dem der Beschluss gehört",
        )

        subparser.add_argument(
            "-b", "--betrag", type=Decimal, help="Der Betrag des Beschlusses"
        )

        subparser.add_argument(
            "-z",
            "--zweck",
            help="Zweckbindung des Beschlusses (z.B: Grillgut Sommerfest)",
            nargs="+",
        )

    def create_resolutions_edit_options(subparser: ArgumentParser):
        subparser.add_argument(
            "beschlussid", help="Zu bearbeitender Beschluss", type=str
        )

        subparser.add_argument(
            "-b", "--betrag", help="Neuer Betrag des Beschlusses", type=Decimal
        )

        subparser.add_argument(
            "-p", "--posten", help="Neuer Posten des Beschlusses", type=str
        )

    def create_resolutions_get_options(subparser: ArgumentParser):
        subparser.add_argument(
            "-p",
            "--posten",
            help="Beschlüsse von Posten p",
            type=str,
        )

        subparser.add_argument(
            "-d", "--datum", help="Beschlüsse von Datum d", type=date_parser
        )

        subparser.add_argument(
            "-z",
            "--zweck",
            help="Verwendungszweck des Beschlusses",
            nargs="+",
        )

    def create_resolutions_options_main(subparser: ArgumentParser):
        new_sub_func = subparser.add_subparsers(dest="resolutions_action")

        resolutions_add = new_sub_func.add_parser("add", help="Füge Beschluss hinzu")
        create_resolutions_add_options(resolutions_add)

        resolutions_edit = new_sub_func.add_parser("edit", help="Bearbeite Beschluss")
        create_resolutions_edit_options(resolutions_edit)

        resolutions_get = new_sub_func.add_parser("get", help="Durchsuche Beschlüsse")
        create_resolutions_get_options(resolutions_get)

        resolutions_delete = new_sub_func.add_parser("delete", help="Lösche Beschlüsse")
        resolutions_delete.add_argument("beschlussid", type=str)

        return (resolutions_add, resolutions_edit, resolutions_get)

    def create_status_options(subparser: ArgumentParser):
        status_sub = subparser.add_subparsers(dest="status_type")
        posten_sub = status_sub.add_parser(
            "posten", help="Zeige Status des aktuellen Postens"
        )
        posten_sub.add_argument(
            "posten",
        )
        status_sub.add_parser("plan", help="Zeige aktuellen Haushaltsplan")
        status_sub.add_parser(
            "noid", help="Zeige alle Transaktionen, die noch keine BeschlussID haben"
        )
        status_sub.add_parser("transactions", help="Zeige alle Transaktionen")
        status_sub.add_parser("transactions_konto", help="alle Transaktionen ohne Bar")
        status_sub.add_parser("resolutions", help="Zeige alle Beschlüsse")

    def create_output_options(subparser: ArgumentParser):
        sub_output = subparser.add_subparsers(dest="output_action")
        kb_sub = sub_output.add_parser("barzahlungen")
        kb_sub.add_argument("outpath", help="Pfad für CSV", type=str)

        rb_sub = sub_output.add_parser(
            "rechenschaftsbericht", help="Erzeuge Rechenschaftsbericht"
        )
        rb_sub.add_argument(
            "dateiname",
            help="Dateiname der Ausgegebenen Exceltabelle",
            type=str,
            default="Rechenschaftsbericht",
        )

        return sub_output

    # ----------------------
    parser = ArgumentParser(prog="finanztool")
    current_year = get_current_year_folder()
    # main options
    parser.add_argument(
        "-y",
        "--year",
        help=f"""
            Das Jahr, in dem gearbeitet werden soll. Wählt Standardmäßig den Ordner in .year, sonst
            Ordner mit der höchsten Zahl aus, der im aktuellen Ordner vorhanden ist und das momentane
            Jahr als letzten Fallback. (Erkannt: {current_year})
        """,
        default=current_year,
        type=str,
    )
    parser.add_argument(
        "-s",
        "--setyear",
        help="""
            Setze das Jahr, welches aktuell verwendet werden soll
        """,
        type=str,
        default=None,
    )
    subparser_func = parser.add_subparsers(
        dest="action",
    )

    sub_status = subparser_func.add_parser(
        "status", help="Statusinformationen zu bisherigen Transaktionen/Haushaltsplan"
    )
    create_status_options(sub_status)
    sub_transactions = subparser_func.add_parser(
        "transactions",
        help="Transaktionen durchführen",
    )
    t_add, t_edit, t_delete, t_get, t_interactive = create_transactions_main(
        sub_transactions
    )
    sub_resolutions = subparser_func.add_parser(
        "resolutions", help="Beschlüsse hinzufügen und bearbeiten"
    )
    r_add, r_edit, r_get = create_resolutions_options_main(sub_resolutions)
    sub_output = subparser_func.add_parser(
        "output", help="Erzeuge Output vom aktuellen Finanzstand"
    )
    create_output_options(sub_output)

    # Weitere Fehlermeldungen/Hilfemeldungen
    if argstr is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argstr.split())

    if args.setyear:
        args.year = args.setyear
        Path(".year").open("w").write(args.setyear)

    match args.action:
        case "transactions":
            match args.transactions_action:
                case None:
                    sub_transactions.print_help()
                    exit(1)
                case "add":
                    if (
                        args.posten is None
                        or args.rechnungsdatum is None  # noqa: W503
                        or args.transaktionsdatum is None  # noqa: W503
                        or args.empfaenger is None  # noqa: W503
                        or args.zweck is None  # noqa: W503
                        or args.betrag is None  # noqa: W503
                    ):
                        print_error(
                            "Alle Optionen von 'transactions add' müssen gesetzt sein!"
                        )
                        t_add.print_help()
                        exit(1)
                    else:
                        args.empfaenger = " ".join(args.empfaenger)
                        args.zweck = " ".join(args.zweck)
                        args.comment = " ".join(args.comment)
        case "resolutions":
            match args.resolutions_action:
                case "add":
                    if (
                        args.datum is None  # noqa: W504
                        or args.posten is None  # noqa: W504
                        or args.betrag is None  # noqa: W504
                        or args.zweck is None
                    ):
                        print_error(
                            "Alle Optionen von 'resolutions add' müssen gesetzt sein!"
                        )
                        r_add.print_help()
                        exit(1)
                    else:
                        args.zweck = (
                            " ".join(args.zweck) if args.zweck is not None else None
                        )

                case "get":
                    args.zweck = (
                        " ".join(args.zweck) if args.zweck is not None else None
                    )

                case "edit":
                    if args.betrag is None and args.posten is None:
                        print_error("Keine Neuen Werte ausgewählt, beende")
                        exit(1)
        case "status":
            match args.status_type:
                case None:
                    sub_status.print_help()
                    exit(1)
        case "output":
            match args.output_action:
                case None:
                    sub_output.print_help()
        case None:
            parser.print_help()
            exit(1)

    return args
