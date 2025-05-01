"""
Überprüfe, ob benötigte Bibliotheken schon auf dem System
installiert sind.
"""
from importlib.util import find_spec
from argparse import ArgumentParser
from sys import executable
from subprocess import check_call


def required_packages() -> [str]:
    with open("./requirements.txt", "r") as handle:
        return [line.split('\n')[0] for line in handle.readlines()]


def install(p: str):
    check_call([
        executable,
        '-m',
        'pip',
        'install',
        p
    ])


def main():
    parser = ArgumentParser()
    parser.add_argument(
        '-i',
        help="installiere fehlende Pakete",
        dest='install',
        action='store_true'
    )
    args = parser.parse_args()

    for p in required_packages():
        if find_spec(p) is None:
            if args.install:
                install(p)
            else:
                print(f"Fehlendes Paket: {p}")

    print("Überprüfung abgeschlossen")


if __name__ == "__main__":
    main()
