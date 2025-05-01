"""
oneshot Aufruf von resolutions als subcommand
"""
from finanztool.lib.files import Tables
from finanztool.lib.tables.resolutions import add_resolution, edit_resolution, get_resolutions, delete_resolution


def resolutions(
    files: Tables,
    args
):
    """
    :param tables: Tables Objekt mit ausgewähltem Jahr
    :param args: Ausgabe das argparsers
    """
    match args.resolutions_action:
        case "add":
            files.beschluesse, b_id = add_resolution(
                files.beschluesse,
                args.datum,
                args.posten,
                args.betrag,
                args.zweck
            )
            print(f"Beschluss mit ID {b_id} hinzugefügt")
            files.save('beschluesse')

        case "get":
            files.pprint(get_resolutions(
                files.beschluesse,
                args.posten,
                args.datum,
                args.zweck
            ))

        case "delete":
            files.beschluesse = delete_resolution(
                files.beschluesse,
                args.beschlussid
            )
            print(f"Beschluss mit ID {args.beschlussid} gelöscht")
            files.save('beschluesse')

        case "edit":
            files.beschluesse = edit_resolution(
                files.beschluesse,
                args.beschlussid,
                args.betrag,
                args.posten
            )
            files.save('beschluesse')
