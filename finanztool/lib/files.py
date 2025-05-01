from pathlib import Path
from shutil import copyfile
from os.path import dirname
from pandas import read_csv, DataFrame
from decimal import Decimal
from datetime import datetime
from tabulate import tabulate
import finanztool

FILES = ["haushaltsplan", "transaktionen", "beschluesse"]


def _isodate(s):
    if s is None:
        return None
    return datetime.strptime(s, "%Y-%m-%d").date()


class Tables:
    def __init__(self, year):
        """
        Lädt Dataframes für spezifiziertes Jahr. Falls Ordner nicht existiert
        wird über Kommandozeile gefragt, ob ein neuer erstellt werden soll.

        Dateizugriff erfolgt als property über den Dateinamen. Bsp:
        files = TableLoader(2023)
        files.haushaltsplan
        """
        global FILES
        # Überprüfe ob Jahresordner exisitert, falls nicht lege nach Sample an
        year_folder = Path("./" + year)
        if not year_folder.exists():
            reply = input(
                f"Ordner '{year}' existiert nicht, soll ein neuer erstellt werden? [j/N] "
            )
            if reply == "j":
                year_folder.mkdir()
                csv_samples_path = Path(dirname(finanztool.__file__) + "/csv_samples")
                for file in csv_samples_path.iterdir():
                    copyfile(file, year_folder.__str__() + "/" + file.name)
            else:
                exit(1)

        # baue dict mit Pfaden
        self._paths = {s: year_folder.joinpath(f"{s}.csv") for s in FILES}

        # überprüfe ob Dateien existieren
        for p in self._paths:
            path = self._paths[p]
            if not path.exists():
                print(f"Datei {path.name} existiert nicht, beende")
                exit(1)

        # Lade Dateien (ungenutzte Converter werden ignoriert)
        self._dataframes = {
            s: read_csv(
                self._paths[s],
                converters={
                    "stand_konto": Decimal,
                    "stand_kasse": Decimal,
                    "stand_gesamt": Decimal,
                    "betrag": Decimal,
                    "rechnungsdatum": _isodate,
                    "transaktionsdatum": _isodate,
                    "beschlussdatum": _isodate,
                    "datum": _isodate,
                    "bemerkung": str,
                    "zweck": str,
                },
            )
            for s in FILES
        }

    def save(self, tablename: str):
        """
        Speichere Tabelle ab.

        :param tablename: Qualifizierter Tabellenname ('haushaltsplan', 'transaktionen', 'beschluesse')
        """
        global FILES
        if tablename not in FILES:
            # kann nur bekannte Dateien speichern
            raise KeyError()
        self._dataframes[tablename].to_csv(self._paths[tablename], index=False)

    def pprint(self, table: str | DataFrame):
        """
        Pretty print der spezifizierten Tabelle.

        :param tablename: Qualifizierter Tabellenname ('haushaltsplan', 'transaktionen', 'beschluesse')
          oder DataFrame
        """
        global FILES

        def _actual_pprint(t):
            print(tabulate(t, headers="keys", tablefmt="simple_grid", showindex=False))

        if isinstance(table, str):
            if table not in FILES:
                raise KeyError()
            if table == "transaktionen":
                _actual_pprint(
                    self._dataframes[table][
                        [
                            "posten",
                            "betrag",
                            "auf_konto",
                            "belegid",
                            "transaktionsdatum",
                            "zweck",
                            "empfaenger",
                            "beschlussid",
                            "stand_konto",
                            "stand_barkasse",
                        ]
                    ]
                )
            else:
                _actual_pprint(self._dataframes[table])
        elif isinstance(table, DataFrame):
            _actual_pprint(table)

    @property
    def haushaltsplan(self):
        return self._dataframes["haushaltsplan"]

    @haushaltsplan.setter
    def haushaltsplan(self, value):
        self._dataframes["haushaltsplan"] = value

    @property
    def transaktionen(self):
        return self._dataframes["transaktionen"]

    @transaktionen.setter
    def transaktionen(self, value):
        self._dataframes["transaktionen"] = value

    @property
    def beschluesse(self):
        return self._dataframes["beschluesse"]

    @beschluesse.setter
    def beschluesse(self, value):
        self._dataframes["beschluesse"] = value
