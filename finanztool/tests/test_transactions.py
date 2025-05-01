from datetime import date
from decimal import Decimal
from finanztool.lib.tables.transactions import add_transaction, delete_transaction  # get_transactions, edit_transaction
from finanztool.tests.common import templates_fixture


@templates_fixture("transaktionen")
def test_add_once(trans):
    d_r = date.fromisoformat("2000-01-01")
    d_t = date.fromisoformat("2000-01-02")
    trans, _ = add_transaction(
        trans,
        "E1.1",
        d_r,
        d_t,
        Decimal("2.02"),
        "Irgendein Zweck",
        "Der FSR",
        True,
        "B20000101001",
        "Nur zum Test"
    )
    assert trans.shape[0] == 1
    assert trans["posten"][0] == "E1.1"
    assert trans["rechnungsdatum"][0] == d_r
    assert trans["transaktionsdatum"][0] == d_t
    assert trans["betrag"][0] == Decimal("2.02")
    assert trans["zweck"][0] == "Irgendein Zweck"
    assert trans["empfaenger"][0] == "Der FSR"
    assert trans["auf_konto"][0]
    assert trans["beschlussid"][0] == "B20000101001"
    assert trans["bemerkung"][0] == "Nur zum Test"
    # überprüfe Berechnungen
    assert trans["stand_konto"][0] == Decimal("2.02")
    assert trans["stand_barkasse"][0] == 0
    assert trans["stand_konto"][0] == trans["stand_gesamt"][0]


@templates_fixture("transaktionen")
def test_add_multi_calc(trans):
    trans, _ = add_transaction(
        trans,
        "E1",
        date.fromtimestamp(0),
        date.fromisoformat("2000-01-02"),
        Decimal("200"),
        "",
        "",
        True,
        full_update=False
    )

    trans, _ = add_transaction(
        trans,
        "A1",
        date.fromtimestamp(0),
        date.fromisoformat("2000-01-03"),
        Decimal("50"),
        "",
        "",
        False
    )
    # erwartet: Kasse -50, Konto 200, gesamt 150

    assert trans["stand_barkasse"][1] == Decimal("-50")
    assert trans["stand_konto"][1] == Decimal("200")
    assert trans["stand_gesamt"][1] == Decimal("150")

    # Transaktion vor Barausnahme -> Bar sollte wieder positiv sein
    trans, _ = add_transaction(
        trans,
        "E1",
        date.fromtimestamp(0),
        date.fromisoformat("2000-01-01"),
        Decimal("100"),
        "",
        "",
        False
    )

    # if this comes up you probably dropped ignore_index
    print(trans[["stand_konto", "stand_barkasse", "stand_gesamt"]])
    assert trans["stand_barkasse"][2] == Decimal("50")
    assert trans["stand_konto"][2] == Decimal("200")
    assert trans["stand_gesamt"][2] == Decimal("250")


@templates_fixture("transaktionen")
def test_delete_updates(trans):
    # Transaktionen von oben
    trans, _ = add_transaction(
        trans,
        "E1",
        date.fromtimestamp(0),
        date.fromisoformat("2000-01-02"),
        Decimal("200"),
        "",
        "",
        True,
        full_update=False
    )

    trans, delid = add_transaction(
        trans,
        "A1",
        date.fromtimestamp(0),
        date.fromisoformat("2000-01-03"),
        Decimal("50"),
        "",
        "",
        False
    )

    trans, _ = add_transaction(
        trans,
        "E1",
        date.fromtimestamp(0),
        date.fromisoformat("2000-01-01"),
        Decimal("100"),
        "",
        "",
        False
    )

    trans = delete_transaction(trans, belegid=delid)
    assert trans.shape[0] == 2
    assert trans["stand_gesamt"][1] == Decimal("300")


@templates_fixture("transaktionen")
def test_edit(trans):
    # TODO
    pass


@templates_fixture("transaktionen")
def test_get(trans):
    # TODO
    pass
