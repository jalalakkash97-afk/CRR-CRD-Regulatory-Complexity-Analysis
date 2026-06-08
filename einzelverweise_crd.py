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


# Definiert eine Hilfsfunktion, die prueft, ob ein gefundener Article-Verweis extern ist.
def ist_externer_artikelverweis(CFR_Text, match_start, match_end, paraend):

    # Schneidet ein kurzes Textfenster direkt nach dem gefundenen Verweis aus.
    context_after = CFR_Text[match_end:min(match_end + 120, paraend)]

    # Schneidet ein Textfenster vor dem gefundenen Verweis aus.
    context_before = CFR_Text[max(0, match_start - 240):match_start]

    # Vereinheitlicht Gross-/Kleinschreibung, damit die Suche stabiler ist.
    context_after_lower = context_after.lower()
    context_before_lower = context_before.lower()

    # Entfernt fuehrende Leerzeichen nach dem gefundenen Article-Verweis.
    context_after_clean = context_after_lower.lstrip()

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
    context_after = CFR_Text[match_end:min(match_end + 160, paraend)]

    # Schneidet ein Textfenster vor dem gefundenen Article-Verweis aus.
    context_before = CFR_Text[max(0, match_start - 240):match_start]

    # Vereinheitlicht Gross-/Kleinschreibung fuer stabile Suche.
    context_after_lower = context_after.lower()
    context_before_lower = context_before.lower()

    # Entfernt fuehrende Leerzeichen nach dem gefundenen Article-Verweis.
    context_after_clean = context_after_lower.lstrip()

    # Prueft auf die direkte CRR-Kennung: Regulation (EU) No 575/2013.
    if "575/2013" in context_after_lower and "regulation" in context_after_lower:

        # Gibt True zurueck, wenn der externe Artikelverweis auf die CRR zeigt.
        return True

    # Prueft Rueckverweise wie "Article 99(1) of that Regulation".
    # Sie zaehlen als CRR-Verweis, wenn kurz vorher Regulation (EU) No 575/2013 genannt wurde.
    if context_after_clean.startswith("of that regulation") and "575/2013" in context_before_lower and "regulation" in context_before_lower:

        # Gibt True zurueck, weil "that Regulation" hier auf die CRR zurueckverweist.
        return True

    # Gibt False zurueck, wenn kein CRR-Hinweis gefunden wurde.
    return False


# Prueft, ob ein Verweis explizit auf die CRD zeigt.
# Gemeint ist hier vor allem die Richtlinie 2013/36/EU.
def ist_crd_artikelverweis(CFR_Text, match_start, match_end, paraend):

    # Schneidet ein Textfenster direkt nach dem gefundenen Article-Verweis aus.
    context_after = CFR_Text[match_end:min(match_end + 160, paraend)]

    # Vereinheitlicht Gross-/Kleinschreibung.
    context_after_lower = context_after.lower()

    # Direkter CRD-Hinweis: Directive 2013/36/EU.
    if "2013/36/eu" in context_after_lower and "directive" in context_after_lower:

        # Gibt True zurueck, wenn der Treffer explizit auf die CRD zeigt.
        return True

    # Andernfalls liegt kein ausdruecklicher CRD-Hinweis vor.
    return False


# Prueft, ob direkt nach dem Artikel auf denselben Rechtsakt verwiesen wird.
# Beispiele:
# - "Article 115 of this Regulation" im CRR
# - "Article 74 of this Directive" im CRD
def ist_verweis_auf_denselben_rechtsakt(CFR_Text, match_end, paraend, current_act):

    # Schneidet ein kurzes Textfenster direkt nach dem gefundenen Verweis aus.
    context_after = CFR_Text[match_end:min(match_end + 120, paraend)]

    # Vereinheitlicht Gross-/Kleinschreibung und entfernt fuehrende Leerzeichen.
    context_after_clean = context_after.lower().lstrip()

    # Im CRR wird derselbe Rechtsakt typischerweise als "this Regulation" bezeichnet.
    if current_act == "CRR" and context_after_clean.startswith("of this regulation"):

        # Gibt True zurueck: interner CRR-Verweis.
        return True

    # In der CRD wird derselbe Rechtsakt typischerweise als "this Directive" bezeichnet.
    if current_act == "CRD" and context_after_clean.startswith("of this directive"):

        # Gibt True zurueck: interner CRD-Verweis.
        return True

    # In allen anderen Faellen liegt kein ausdruecklicher Gleich-Rechtsakt-Hinweis vor.
    return False


# Definiert die eigentliche Funktion zur Suche einfacher Artikelverweise.
# Die neuen Parameter werden zunaechst optional gehalten, damit der bisherige
# Aufruf aus main.py vorerst weiter funktioniert.
#
# current_act:
#   Kennzeichnet den Quellrechtsakt des aktuell bearbeiteten Artikels
#   (spaeter typischerweise "CRD" oder "CRR").
#
# ParagraphList_CRD / ParagraphList_CRR:
#   Enthalten die reinen Artikelnummern beider Rechtsakte. Sie werden spaeter
#   benoetigt, um gefundene Verweise sauber als CRD-, CRR- oder externe
#   Verweise einzuordnen.
def einzelverweise_crd(
    ParagraphSign,
    parabegin,
    paraend,
    CFR_Text,
    ParagraphList,
    current_paragraph,
    current_act=None,
    ParagraphList_CRD=None,
    ParagraphList_CRR=None,
):

    # Uebergangsregel:
    # Solange main.py noch nicht beide Rechtsakte getrennt an die Funktion uebergibt,
    # wird ohne explizite Angabe weiter vom bisherigen CRD-Fall ausgegangen.
    if current_act is None:
        current_act = "CRD"

    # Falls die beiden Artikellisten noch nicht separat uebergeben wurden,
    # wird fuer den Uebergangsstand die bisherige ParagraphList als Liste des
    # aktuellen Rechtsakts verwendet. Dadurch bleibt der bisherige CRD-Lauf intakt.
    if ParagraphList_CRD is None and current_act == "CRD":
        ParagraphList_CRD = ParagraphList
    if ParagraphList_CRR is None and current_act == "CRR":
        ParagraphList_CRR = ParagraphList

    # Neue Ergebnislisten fuer die kuenftige Zielstruktur.
    # Sie werden in diesem Zwischenschritt bereits angelegt, auch wenn die
    # vollstaendige Klassifikationslogik erst in den naechsten Schritten folgt.
    #
    # Verweise_Berechnung:
    #   Alle internen Verweise im gemeinsamen System CRD + CRR.
    #   Diese Liste soll spaeter in die eigentliche Komplexitaetsberechnung eingehen.
    Verweise_Berechnung = []

    # Verweise_gleicher_Rechtsakt:
    #   Verweise innerhalb desselben Rechtsakts, also spaeter z. B. CRD -> CRD
    #   oder CRR -> CRR.
    Verweise_gleicher_Rechtsakt = []

    # Verweise_anderer_Rechtsakt:
    #   Verweise zwischen den beiden internen Rechtsakten, also spaeter
    #   CRD -> CRR oder CRR -> CRD.
    Verweise_anderer_Rechtsakt = []

    # Verweise_extern:
    #   Verweise auf andere Rechtsakte ausserhalb des Systems CRD + CRR.
    Verweise_extern = []

    # Verweise_gesamt:
    #   Sammelliste aller erkannten Einzelverweise des aktuellen Artikels.
    Verweise_gesamt = []

    # Alte Listen bleiben in diesem Zwischenschritt noch als Alias erhalten,
    # damit die bisherige Rueckgabe und die aktuelle Logik aus main.py noch
    # nicht sofort umgestellt werden muessen.
    Einzelverweise = Verweise_Berechnung
    ExterneEinzelverweise = Verweise_extern
    CRREinzelverweise = Verweise_anderer_Rechtsakt

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

        # Speichert jeden erkannten Einzelverweis zunaechst in der Gesamtliste.
        # Die eigentliche Klassifikation folgt erst in den naechsten Pruefschritten.
        Verweise_gesamt.append(verweis)

        # Eigenverweise werden nicht gezaehlt.
        if verweis == current_paragraph:

            # Springt zum naechsten Treffer.
            continue

        # Ab hier wird aktabhaengig klassifiziert.
        # Die Logik unterscheidet bewusst zwischen CRD- und CRR-Artikeln,
        # weil der Standardfall ohne Marker jeweils anders zu deuten ist.

        # Fall A: aktueller Artikel stammt aus der CRD.
        if current_act == "CRD":

            # Expliziter Verweis von CRD auf die CRR.
            if ist_crr_artikelverweis(CFR_Text, match_start, match_end, paraend):

                # Nur Artikel uebernehmen, die in der CRR-Artikelliste vorkommen.
                if ParagraphList_CRR is not None and verweis in ParagraphList_CRR:

                    ziel = "CRR_" + verweis

                    # Fuer die Berechnung zaehlt der Verweis als interner Verweis
                    # im gemeinsamen System CRD + CRR.
                    Verweise_Berechnung.append(ziel)

                    # Fuer die Statistik wird er als Verweis auf den anderen Rechtsakt erfasst.
                    Verweise_anderer_Rechtsakt.append(ziel)

                # Geht danach direkt zum naechsten Treffer.
                continue

            # Explizite Verweise auf andere Rechtsakte bleiben extern.
            if ist_externer_artikelverweis(CFR_Text, match_start, match_end, paraend):

                # Speichert den Treffer als externen Verweis.
                Verweise_extern.append(verweis)
                continue

            # "of this Directive" bestaetigt einen internen CRD-Verweis.
            if ist_verweis_auf_denselben_rechtsakt(CFR_Text, match_end, paraend, current_act):

                if ParagraphList_CRD is not None and verweis in ParagraphList_CRD:

                    ziel = "CRD_" + verweis
                    Verweise_Berechnung.append(ziel)
                    Verweise_gleicher_Rechtsakt.append(ziel)

                continue

            # Standardfall ohne Marker:
            # Im CRD wird der Treffer als interner CRD-Verweis behandelt,
            # sofern die Artikelnummer in der CRD-Artikelliste vorkommt.
            if ParagraphList_CRD is not None and verweis in ParagraphList_CRD:

                ziel = "CRD_" + verweis
                Verweise_Berechnung.append(ziel)
                Verweise_gleicher_Rechtsakt.append(ziel)

                continue

            # Falls der Treffer weder intern zugeordnet noch explizit als CRR-Verweis
            # erkannt wurde, bleibt er fuer den Moment extern.
            Verweise_extern.append(verweis)
            continue

        # Fall B: aktueller Artikel stammt aus dem CRR.
        if current_act == "CRR":

            # Expliziter Verweis von CRR auf die CRD.
            if ist_crd_artikelverweis(CFR_Text, match_start, match_end, paraend):

                # Nur Artikel uebernehmen, die in der CRD-Artikelliste vorkommen.
                if ParagraphList_CRD is not None and verweis in ParagraphList_CRD:

                    ziel = "CRD_" + verweis
                    Verweise_Berechnung.append(ziel)
                    Verweise_anderer_Rechtsakt.append(ziel)

                continue

            # Explizite Verweise auf andere Rechtsakte bleiben extern.
            if ist_externer_artikelverweis(CFR_Text, match_start, match_end, paraend):

                Verweise_extern.append(verweis)
                continue

            # "of this Regulation" bestaetigt einen internen CRR-Verweis.
            if ist_verweis_auf_denselben_rechtsakt(CFR_Text, match_end, paraend, current_act):

                if ParagraphList_CRR is not None and verweis in ParagraphList_CRR:

                    ziel = "CRR_" + verweis
                    Verweise_Berechnung.append(ziel)
                    Verweise_gleicher_Rechtsakt.append(ziel)

                continue

            # Standardfall ohne Marker:
            # Im CRR wird der Treffer als interner CRR-Verweis behandelt,
            # sofern die Artikelnummer in der CRR-Artikelliste vorkommt.
            if ParagraphList_CRR is not None and verweis in ParagraphList_CRR:

                ziel = "CRR_" + verweis
                Verweise_Berechnung.append(ziel)
                Verweise_gleicher_Rechtsakt.append(ziel)

                continue

            # Alles, was danach noch uebrig bleibt, wird vorerst extern erfasst.
            Verweise_extern.append(verweis)
            continue

    # Gibt interne, externe und davon CRR-bezogene Einzelverweise getrennt an main.py zurueck.
    #
    # Uebergangsstand:
    # main.py erwartet aktuell noch drei Rueckgabewerte. Deshalb werden hier
    # vorerst die entsprechenden Teilmengen der neuen Struktur zurueckgegeben:
    #
    # - Einzelverweise            -> interne Verweise fuer die Berechnung
    # - ExterneEinzelverweise     -> externe Verweise
    # - CRREinzelverweise         -> Verweise auf den jeweils anderen internen Rechtsakt
    return Einzelverweise, ExterneEinzelverweise, CRREinzelverweise

