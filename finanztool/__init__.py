from finanztool.argparser import parse_args
from finanztool.lib.files import Tables
from finanztool.lib.commands import transactions, resolutions, status, output


def main():
    args = parse_args()
    files = Tables(args.year)

    match args.action:
        case "transactions":
            transactions(files, args)

        case "resolutions":
            resolutions(files, args)

        case "status":
            status(files, args)

        case "output":
            output(files, args)
