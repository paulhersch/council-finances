from finanztool.lib.files import Tables
from finanztool.lib.tables.virtual import plan_bilanz, beschluesse_bilanz
from pandas import ExcelWriter, Series, DataFrame
from tabulate import tabulate
from decimal import Decimal
from pathlib import Path
from typing import List


def output(tables: Tables, args):
    """
    :param tables: Tables Objekt des ausgewählten Jahres
    :param args: Rückgabe des argparsers
    """
    match args.output_action:
        case "rechenschaftsbericht":
            with ExcelWriter(
                args.dateiname,
                mode="w",
                engine="xlsxwriter",
                engine_kwargs={"options": {"strings_to_numbers": True}},
            ) as writer:
                wb = writer.book
                # Währungsformat für Deutschland in Excel
                # . und , MÜSSEN vertauscht sein, durch die Interpretation
                # der LOCALE-Einstellungen wird das in Excel/LibreOffice "zurück" getauscht.
                euro_fmt_str = "#,##0.00 [$€-407];[Red]-#,##0.00 [$€-407]"
                euro_fmt = wb.add_format({"num_format": euro_fmt_str})

                # Haushaltsplan/Rechenschaftsbericht
                virtual_plan = plan_bilanz(tables.haushaltsplan, tables.transaktionen)

                # Bestimmung von Indizes für Positionen der Zwischenbilanzen
                only_e = virtual_plan.set_index(
                    "posten", drop=True, inplace=False
                ).filter(like="E", axis=0)
                e_end_row = only_e.shape[0] + 1

                only_a = virtual_plan.set_index(
                    "posten", drop=True, inplace=False
                ).filter(like="A", axis=0)
                a_end_row = virtual_plan.shape[0] + 1

                # Zwischenbelanzen precalc für Kompatibilität bei write unten
                def _precalc_bilanz(df: DataFrame):
                    betrag = Decimal(0)

                    def _to_apply(row: Series):
                        nonlocal betrag
                        betrag += row.real

                    df.apply(_to_apply, axis=1)
                    return betrag

                bilanz_e = _precalc_bilanz(only_e)
                bilanz_a = _precalc_bilanz(only_a)
                # Header umbenennen, damit die Stura-Finanzys happy sind
                virtual_plan.rename(
                    columns={
                        "posten": "Posten",
                        "titel": "Bezeichnung",
                        "betrag": "Geplant",
                        "real": "Real gebucht",
                        "diff": "Differenz",
                    },
                    inplace=True,
                )
                virtual_plan.to_excel(writer, index=False, sheet_name="Übersicht")

                # Formatierung der Betragszellen
                plan_sheet = writer.sheets["Übersicht"]
                plan_sheet.autofit()
                plan_sheet.set_column("C:E", 15, cell_format=euro_fmt)

                # Erstelle Zwischenbilanzen bei G
                plan_sheet.set_column("G:G", 20)  # Breite der Spalte
                zwischen_farbe = wb.add_format({"bg_color": "#dee7e5"})  # dee7e5
                zwischen_zahl = wb.add_format(
                    {"bg_color": "#dee7e5", "num_format": euro_fmt_str}
                )
                plan_sheet.write(f"G{e_end_row-1}", "Zwischensumme", zwischen_farbe)
                plan_sheet.write_formula(
                    f"G{e_end_row}", f"=SUM(D2:D{e_end_row})", zwischen_zahl, bilanz_e
                )

                plan_sheet.write(f"G{a_end_row-1}", "Zwischensumme", zwischen_farbe)
                plan_sheet.write(
                    f"G{a_end_row}",
                    f"=SUM(D{e_end_row+1}:D{a_end_row})",
                    zwischen_zahl,
                    bilanz_a,
                )
                # # Erstelle Finale Bilanz (Ausgleich)
                # end_farbe = wb.add_format({"bg_color": "#f6f9d4"})  # f6f9d4

                # Transaktionen
                trans_df = tables.transaktionen[
                    [
                        "belegid",
                        "posten",
                        "betrag",
                        "rechnungsdatum",
                        "transaktionsdatum",
                        "stand_konto",
                        "stand_barkasse",
                        "auf_konto",
                        "empfaenger",
                        "zweck",
                    ]
                ]

                def _betrag_negative_if_outgoing(row: Series) -> Series:
                    if row.posten[0] == "A":
                        row.betrag = -row.betrag
                    return row

                trans_df = trans_df.apply(_betrag_negative_if_outgoing, axis=1)

                # Trenne nach Kasse und Konto
                trans_bar_df = trans_df.query("not auf_konto").drop(
                    ["auf_konto", "stand_konto"], axis=1
                )
                trans_konto_df = trans_df.query("auf_konto").drop(
                    ["auf_konto", "stand_barkasse"], axis=1
                )

                # Fancy Header wie beim Plan
                def set_fancy_headers(df: DataFrame):
                    df.rename(
                        inplace=True,
                        columns={
                            "belegid": " Belegnummer ",
                            "posten": " Posten ",
                            "betrag": " Betrag ",
                            "rechnungsdatum": " Rechnungsdatum ",
                            "transaktionsdatum": " Transaktionsdatum ",
                            "stand_barkasse": " Kassenstand ",
                            "stand_konto": " Kontostand ",
                            "empfaenger": " Empfänger ",
                            "zweck": " Verwendungszweck ",
                        },
                    )

                set_fancy_headers(trans_bar_df)
                set_fancy_headers(trans_konto_df)

                # Sheets schreiben und formatieren
                trans_bar_df.to_excel(
                    writer, index=False, sheet_name="Transaktionen Kasse"
                )
                trans_bar_sheet = writer.sheets["Transaktionen Kasse"]

                trans_konto_df.to_excel(
                    writer, index=False, sheet_name="Transaktionen Konto"
                )
                trans_konto_sheet = writer.sheets["Transaktionen Konto"]

                def format_sheet(sheet):
                    sheet.autofit()
                    # Breite etwas weiter, damit die Zahlen komplett Platz haben
                    sheet.set_column("C:C", 15, cell_format=euro_fmt)
                    sheet.set_column("F:F", 15, cell_format=euro_fmt)

                format_sheet(trans_bar_sheet)
                format_sheet(trans_konto_sheet)

        case "barzahlungen":
            outpath = Path(args.outpath)
            tab_nur_bar = tables.transaktionen.query("not auf_konto")[
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
            tab_nur_bar.to_csv(outpath, index=False)
