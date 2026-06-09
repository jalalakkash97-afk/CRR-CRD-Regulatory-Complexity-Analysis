'''Version: 07.05.2026
Funktion zur Identifizierung einfacher interner Artikelverweise in CRD/CRR-Texten.

Diese Datei ist die CRD-Anpassung von einzelverweise.py.
Sie erkennt zunaechst nur einfache Verweise wie "Article 30" oder "Article 4(1)".
Mehrfachverweise wie "Articles 74 and 75" werden spaeter separat behandelt.
'''
# ich musste für die Einzelverweise eigene Datei anrichten, da die "Atrikel" könnte sowohl intern oder extern sein
# bzw. das hier würde Atrikel aus dem CRR auch als ein interner Verweis erkennen, weil Artikel 4 existierst sowhl im CRR als auch im CRD 
# und ich musste jz schon zwischen Internen und externen Verweisen abgrenzen, da über einen einfachen Vergleich in der Liste vom CRD würde ich nicht erkennen 
# ob es intern oder extern ist.
# Importiert regulaere Ausdruecke; damit koennen Artikelverweise flexibler erkannt werden.
import re


# Normalisiert kurze Textausschnitte, damit Zeilenumbrueche die Erkennung nicht stoeren.
def normalisiere_kontext(text):

    # Macht aus Zeilenumbruechen normale Leerzeichen.
    text = text.replace("\n", " ")

    # Entfernt Leerzeichen direkt nach einem Schraegstrich, z.B. "575/ 2013".
    text = re.sub(r"/\s+", "/", text)

    # Fasst mehrere Leerzeichen zu einem Leerzeichen zusammen.
    text = " ".join(text.split())

    # Gibt den vereinheitlichten Text in Kleinschreibung zurueck.
    return text.lower()


# Definiert eine Hilfsfunktion, die prueft, ob ein gefundener Article-Verweis extern ist.
def ist_externer_artikelverweis(CFR_Text, match_start, match_end, paraend):

    # Schneidet ein kurzes Textfenster direkt nach dem gefundenen Verweis aus.
    context_after = CFR_Text[match_end:min(match_end + 120, paraend)]

    # Schneidet ein Textfenster vor dem gefundenen Verweis aus.
    context_before = CFR_Text[max(0, match_start - 240):match_start]

    # Vereinheitlicht den Text, damit Zeilenumbrueche zwischen "of" und "Regulation" nicht stoeren.
    context_after_clean = normalisiere_kontext(context_after)
    context_before_lower = normalisiere_kontext(context_before)

    # Definiert starke Hinweise darauf, dass der Artikel zu einem anderen Rechtsakt gehoert.
    external_markers = [
        "of regulation",
        "of directive",
        "of decision",
        "of delegated regulation",
        "of implementing regulation",
    ]

    # Geht alle externen Hinweise durch.
    for marker in external_markers:

        # Wenn einer dieser Hinweise direkt nach dem Artikel steht, ist der Verweis extern.
        if context_after_clean.startswith(marker):

            # Gibt True zurueck: Der Treffer soll nicht als interner CRD-Verweis zaehlen.
            return True

    # Erkennt Rueckverweise wie "of that Regulation".
    # Das ist extern, wenn kurz vorher bereits eine Regulation genannt wurde.
    if context_after_clean.startswith("of that regulation") and "regulation" in context_before_lower:

        # Gibt True zurueck, weil "that Regulation" auf einen zuvor genannten externen Rechtsakt verweist.
        return True

    # Wenn kein externer Hinweis gefunden wurde, wird der Treffer nicht als extern markiert.
    return False


# Definiert eine Hilfsfunktion, die prueft, ob ein externer Artikelverweis auf die CRR zeigt.
def ist_crr_artikelverweis(CFR_Text, match_start, match_end, paraend):

    # Schneidet ein Textfenster direkt nach dem gefundenen Article-Verweis aus.
    context_after = CFR_Text[match_end:min(match_end + 220, paraend)]

    # Schneidet ein Textfenster vor dem gefundenen Article-Verweis aus.
    context_before = CFR_Text[max(0, match_start - 240):match_start]

    # Vereinheitlicht die Textfenster fuer stabile Suche.
    context_after_clean = normalisiere_kontext(context_after)
    context_before_lower = normalisiere_kontext(context_before)

    # Prueft auf direkte CRR-Kennung direkt nach dem Treffer.
    # Beispiele:
    # Article 4(1) of Regulation (EU) No 575/2013
    # Article 4 (1) of Regulation (EU) No 575/2013
    # Article 259(3) of Regulation (EU) No 575/2013
    if (
        context_after_clean.startswith("of regulation")
        or context_after_clean.startswith("of the regulation")
        or re.match(r"^\(\d+\) of regulation", context_after_clean)
    ) and "575/2013" in context_after_clean:

        # Gibt True zurueck, wenn der externe Artikelverweis auf die CRR zeigt.
        return True

    # Prueft Rueckverweise wie "Article 99(1) of that Regulation".
    # Sie zaehlen als CRR-Verweis, wenn kurz vorher Regulation (EU) No 575/2013 genannt wurde.
    if context_after_clean.startswith("of that regulation") and "575/2013" in context_before_lower and "regulation" in context_before_lower:

        # Gibt True zurueck, weil "that Regulation" hier auf die CRR zurueckverweist.
        return True

    # Prueft Faelle, in denen mehrere Article-Verweise in einem Definitionspunkt stehen
    # und erst am Ende steht, dass sie sich auf Regulation (EU) No 575/2013 beziehen.
    # Beispiel in CRD Artikel 3, Punkt (59): Article 143, Article 221, Article 225, ...
    segment_end = paraend
    for marker in [".", ";"]:
        marker_pos = CFR_Text.find(marker, match_end, paraend)
        if marker_pos != -1:
            segment_end = min(segment_end, marker_pos)

    # Liest nur den aktuellen Satz/Definitionspunkt ab dem gefundenen Verweis.
    segment_after = normalisiere_kontext(CFR_Text[match_end:segment_end])

    # Wenn in diesem engen Abschnitt explizit die CRR genannt wird, kann der Verweis zur CRR gehoeren.
    # Diese Regel soll nur bei Aufzaehlungen greifen, z.B.:
    # Article 143(1), ... Article 225, ... Article 312(2), ... Article 259(3) of Regulation ...
    # Dadurch werden Faelle wie "Article 31 shall apply ... Article 4 of Regulation ..." nicht falsch als CRR erkannt.
    if context_after_clean.startswith(",") and "575/2013" in segment_after and "regulation" in segment_after:

        # Gibt True zurueck, weil der Verweis im selben Abschnitt auf die CRR bezogen wird.
        return True

    # Gibt False zurueck, wenn kein CRR-Hinweis gefunden wurde.
    return False


# Definiert die eigentliche Funktion zur Suche einfacher CRD-Artikelverweise.
def einzelverweise_crd(ParagraphSign, parabegin, paraend, CFR_Text, ParagraphList, current_paragraph):

    # Erstellt eine leere Liste fuer alle internen Einzelverweise im aktuellen Artikel.
    Einzelverweise = []

    ExterneEinzelverweise = []

    # Erstellt eine leere Liste fuer externe Einzelverweise, die speziell auf die CRR zeigen.
    CRREinzelverweise = []

    # Baut ein Suchmuster fuer einfache Artikelverweise.
    # Beispiel: ParagraphSign = "Article" erkennt "Article 30" und "Article 30(2)".
    # "\b" Wortgrenze: sorgt dafür, dass Artikel als einzelwort erkannt wird und nicht mitten im Wort iwo 
    # re.escape sorgt dafür,dass Sondernzeichen als Sonderzeichen erkannt werden im Regex und nicht anders interpritiert( für Artokel ist es überflüssig) 
    #\S+ ein oder mehrere Leezeichen nach dem Wortartikel oder andere zwischen räume
    #\d+  bedeutet eine Ziffer oder mehrere Ziffern () speichern dann diese Ziffer ist wichtig für die Artikel nummer
    #(?:\([^)]+\)) erlaube danch die Klammerangaben aber speicht die nihct als eignes ergebnis
    # ?:  bedeutet gruppe nicht speichern.
    # * null mal einmal oder mehrmal
    pattern = r"\b" + re.escape(ParagraphSign) + r"\s+(\d+)(?:\([^)]+\))*"

    # Sucht alle Treffer des Musters im aktuellen Artikelbereich.
    # Für jeden Treffer, den Regex im Text findet, nenne diesen Treffer kurz MATCH und führe den eingerückten Code aus.
    # Group 0 ist der gesamte gefundene Text, also z.B. "Article 30(2)". Group 1 ist die erste  Klammer im regex Muster(\d+), also die reine Artikelnummer "30". 
    # group 2 wäre die zweite Klammer, also die Klammerangabe"(2)", aber die speichern wir ja nicht als eigenständigen Verweis, sondern nur die Artikelnummer.
    # 
    for match in re.finditer(pattern, CFR_Text[parabegin:paraend]):

        # Holt die gefundene Artikelnummer aus der ersten Klammer des Suchmusters.
        verweis = match.group(1)

        # Rechnet die relative Trefferposition im Artikelausschnitt in die absolute Textposition um.
        match_start = parabegin + match.start()
        match_end = parabegin + match.end()

        # Eigenverweise werden nicht gezaehlt.
        if verweis == current_paragraph:

            # Springt zum naechsten Treffer.
            continue

        # CRR-Verweise werden vor CRD-internen Verweisen geprueft.
        if ist_crr_artikelverweis(CFR_Text, match_start, match_end, paraend):

            # Speichert CRR-Verweise separat fuer die spaetere Anzahl der CRR-Verweisungen.
            CRREinzelverweise.append(verweis)

            # Springt zum naechsten Treffer, weil CRR-Verweise nicht in die CRD-internen Verweise sollen.
            continue

        # Externe Artikelverweise, z. B. auf eine andere Regulation oder Directive, werden nicht uebernommen.
        if ist_externer_artikelverweis(CFR_Text, match_start, match_end, paraend):

            # Speichert nur echte externe Verweise auf andere Rechtsakte separat.
            ExterneEinzelverweise.append(verweis)

            # Springt zum naechsten Treffer, weil externe Verweise nicht in ParagraphVerweise sollen.
            continue

        # Verweise auf Artikel, die nicht in ParagraphList vorkommen, werden nicht als interne Verweise uebernommen.
        if verweis not in ParagraphList:

            # Springt zum naechsten Treffer.
            continue

        # Wenn der Treffer intern ist, wird er in die Ergebnisliste aufgenommen.
        Einzelverweise.append(verweis)

    # Gibt interne, externe und davon CRR-bezogene Einzelverweise getrennt an main.py zurueck.
    return Einzelverweise, ExterneEinzelverweise, CRREinzelverweise

