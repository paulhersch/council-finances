<!-- LTeX: language=de-DE -->
# CLI Tool to manage the student councils finances

I created this to mange the finances of my student council, because i didn't
want to use Excel. In hindsight this would have been a lot easier. Most of the
codebase is a three day hackjob. The most important idea for this thing was
that i was too lazy to always check when we passed resolutions for spending for
the Excel Sheet, so instead i wanted to have a tool where i can also add those
in and then easily check spending on a resolution (because we must not spend
more than decided by the whole council). I also wanted to have an overview on
the spending over the whole year (we have to categorize each expenditure) and
an option to export my non-Excel data store into Excel Worksheets that the
higher student council is happy with, when checking on our finances.

I only translated shorter passages from the README into English because i wrote
a lot of shit down. The tool also lives on our internal git with the whole data
(aka folders with CSVs), so there aren't really going to be updates here.

## Developement/Installation

You can install the dependencies with anything you can use to install stuff
from a requirements.txt. I personally use nix, so i wrote a flake that parses
this file, and an install checker in case you want to use Your user/global
python env.

## Roadmap (Planned before i stopped working on it because it works good enough for me) (German, cba to translate)
 - [x] Eintragen von Rechnungen als oneshot Befehlsaufruf
   - [x] automatische Berechnung von Gesamtkontostand nach Eingabe Kasse + Konto
   - [x] CSV entsprechend Specs ausfüllen
   - [x] beliebiges Transaktionsdatum, Transaktion wird automatisch an korrekter Stelle eingefügt
 - [x] Erlaube Bearbeiten der Daten
  - [x] Beschlüsse bearbeiten
  - [x] Transaktionen bearbeiten
  - [ ] Haushaltsplan bearbeiten(?)
 - [ ] UNITTESTS
 - [ ] Informationsausgabe
   - [x] aktueller Stand eines Kostenpunktes aus Haushaltsplan
   - [x] Aktueller Stand eines Beschlusses (aktuelle Ausgaben, freie Mittel, ...)
   - [ ] Bericht über monatliche Transaktionen
   - [x] Rechenschaftsbericht, sortiert nach Kostenpunkt und Datum
 - [ ] Eintragen von Transaktionen interaktiv
   - [ ] Bereits verwendete Zahlungsempfänger per Zahl auswählen
   - [ ] Eingabe Datum im europäischen Format und automatische Umwandlung
 - [x] Erstellung neuer Jahresordner unter Nutzung der csv_samples
  - [] CSV-Samples zum Formen der aktuellen csv nutzen?
 - [ ] Automatisches comitten via cmdline git (einheitliche Commitmessages)
 - [x] Output Rechenschaftsbericht als .xlsx
 - [ ] Visualisierungen(?)
 - [ ] Irgendein langfristiger Datascience shit(?)

## Yearly management

For every year, a folder is simply created. You can set the default folder with the `-s` option.

## CSV spec (cba to translate this as well)
Spec V5:
 - `haushaltsplan.csv`
   - `posten`: ID des Postens, z.B. "E1.2"
   - `titel`: Menschlich verständlicher Titel des Postens
   - `betrag`: Wie viel Geld in Euro (Abhängig von Posten wird dieser Betrag in Rechnungen als Einnahme oder Ausgabe gewertet)
 - `transaktionen.csv`
    - `posten`: Der Posten, von dem abgerechnet werden soll
    - `belegid`: Interner Index, Vorgabe: "(E|A)JJJJMMTT\<ID\>" wobei "ID" fortlaufend für den Tag gewählt wird und **dreistellig** ist.
    - `rechnungsdatum`: Rechnungsdatum im **amerikanischen** Format (zur Sortierung): "JJJJ-MM-TT". Beim Export wird dieses Format in die entsprechende europäische Variante umgewandelt (damit der KPA happy ist).
    - `transaktionsdatum`: Datum der Überweisung, Format siehe Rechnungsdatum
    - `beschlussid`: Beschluss für Transaktion. Darf zum Erstellzeitpunkt keinen Wert haben, aber sollte zeitnah per `edit` hinzugefügt werden
    - `empfaenger`: Empfängerbezeichner als string, soll der gesamte Name sein.
    - `zweck`: Rechnungszweck, Sollte mit Beschluss übereinstimmen. Falls Transaktion zu 100% Beschluss wiederspiegelt (also keine zwei Transaktionen für den gleichen Beschluss existieren), bitte mit "Beschluss: " beginnen
    - `betrag`: Geldbetrag der Transaktion
    - `stand_konto`: Kontostand auf der Bank nach Transaktion (€), Format: Zahl mit zwei Nachkommastellen
    - `stand_barkasse`: Kontostand der Barkasse nach Transaktion (€), Format siehe `stand_konto`
    - `stand_gesamt`: Gesamt (Bar + Konto) in €, Format siehe `stand_konto`
    - `auf_konto`: Ob Transaktion auf Konto (true) oder Barkasse (false) gebucht wird
    - `bemerkung`: Kommentar zur Transaktion
 - `beschluesse.csv`
  - `datum`: Datum, wann Beschluss verabschiedet wurde
  - `posten`: Der Posten, zu dem der Beschluss gezählt wird
  - `betrag`: Beschlossene auszugebende Geldmenge für Beschluss
  - `zweck`: Verwendungszweck des Beschlusses
  - `beschlussid`: ID für Beschluss, Bildungsvorschrift analog belegid: `BJJJJMMTT\<ID\.>`
### sonstiges
 - Falls keine IDs angegeben (z.B. Für BeschlussID) muss vom Programm "noID" hinterlegt werden. Dadurch können die Einträge ohne IDs später gefunden werden
 - Die Spalten stand_konto, stand_barkasse und stand_gesamt werden erst gesetzt, wenn `update_balances` aus `lib.transactions` genutzt wird oder `transactions_add`
   mit `full_update = True` (default). Bei neu eingefügten Spalten ist der Kontostand sonst 0.

## Aufrufe (mittlerweile unvollständig, überprüfe -h einzelner Unterbefehle!) (Too long for me to translate)
folgender Aufruf + Subkommandos soll implementiert werden
```
finanz_tool [-y JAHR] [-s YEAR] [Subcommand]
  -y    Welches Jahr in den aktuellen Subcommands verwendet werden soll
  -s    Setze das momentan preferierte Jahr (schreibt .year Datei)
```
wobei Subcommand folgendes sein kann
```
  status                Statusberichte
  transactions          Transaktionen verwalten
  resolutions           Beschlüsse verwalten
  output                Verschiedene Outputs generieren
```
(TODO: mehr Optionen für z.B. Jahresübertrag o.ä.)

Die Subcommands haben außerdem Optionen
```
status:
    posten POSTEN       Zeigt Transaktionen die auf POSTEN verrechnet wurden
    plan                Zeigt aktuellen Haushaltsplan als Tabelle
    noid                Zeige alle Transaktionen, die noch keine BeschlussID haben
    transactions        Zeige alle Transaktionen
    resolutions         Zeige alle Beschlüsse

transactions
    add                 Füge Transaktion oneshot hinzu
      Optionen:
        -p POSTEN       Posten
        -r DATUM        Rechnungsdatum
        -t DATUM        Transaktionsdatum
        -i ID           BeschlussID
        -e EMPFAENGER   Empfänger der Transaktion
        -z ZWECK        Verwendungszweck
        -b BETRAG       Betrag der Transaktion
        -c KOMMENTAR    Kommentar zur Transaktion
        -k              Ob Betrag auf Konto gebucht werden soll (default: Barkasse)
    
    edit                Bearbeite Einträge
        belegid         BelegID der Transaktion
      Optionen:
        -i ID           BeschlussID der Transaktion

    delete              Lösche Einträge
        belegid         BelegID der Transaktion

    get
      Optionen (Filter)
        -p POSTEN       Transaktionen mit Posten POSTEN
        -r DATUM        Transaktionen mit Rechnungsdatum DATUM
        -t DATUM        Transaktionen mit Transaktionsdatum DATUM
        -i ID           Transaktionen mit Beschlussid ID
        -e EMPFAENGER   Transaktionen mit Empfänger EMPFAENGER
        -z ZWECK        Transaktionen mit Verwendungszweck ZWECK
    
    interactive         Nutze den interaktiven Modus

resolutions
    add                 Füge einen Beschluss hinzu
      Optionen:
        -d DATUM        Beschlussdatum
        -p POSTEN       ID des Postens, zu dem Beschluss gehört
        -b BETRAG       Der Betrag des Beschlusses
        -z ZWECK        Zweckbindung des Beschlusses (z.B. Grillgut Sommerfest)
    
    edit [beschlussid]  Bearbeite Beschluss
      -b BETRAG         Neuer Betrag des Beschlusses
      -p POSTEN         Neuer Posten des Beschlusses

    delete [beschlussid] Lösche Beschluss

    get
      Optionen (Filter)
        -p POSTEN       Beschlüsse von Posten POSTEN
        -d DATUM        Beschlüsse von Datum DATUM
        -z ZWECK        Beschlüsse mit Zweck ZWECK
output
    rechenschaftsbericht
      FORMAT            Format, in dem der Rechenchaftsbericht ausgeben werden soll.
```


## Wie kriege ich den Haushaltsplan hier rein?
1. Öffne Excel oder sonstiges Tabellenkalkulationsprogramm, welches in CSV exportieren kann
2. Erstelle den Haushaltsplan mit den entsprechend Spezifikation vorgegebenen Spalten
3. Exportiere den Plan als CSV
4. Generiere den Ordner für das neue Jahr mit z.B. `-y 2023 new`
5. Ersetze `plan.csv` im Jahresordner mit der exportierten CSV
