'''Version: 23.04.2026
Funktion zum Laden des regulatorischen Textes

'''
def load_text(file_name):
    # Einzelne EUR-Lex-Exporte enthalten in Tabellen wenige fehlerhafte Bytes.
    # Sie werden zunaechst sichtbar ersetzt und danach in Leerzeichen umgewandelt.
    # So werden benachbarte Woerter oder Zahlen nicht unbemerkt zusammengezogen.
    with open(file_name, "r", encoding="utf-8", errors="replace") as fobj:
        CFR_Text = fobj.read()

    return CFR_Text.replace("\ufffd", " ")
