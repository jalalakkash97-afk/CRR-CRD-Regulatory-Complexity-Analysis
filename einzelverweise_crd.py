"""Version: 08.06.2026
Einfache Erkennung von Einzelverweisen auf Artikelebene fuer CRD- und CRR-Texte.

Ziel der Funktion:
- Einzelverweise wie "Article 30" oder "Article 30(2)" erkennen
- auf Artikelebene reduzieren
- zwischen
  * gleichem Rechtsakt,
  * anderem internen Rechtsakt (CRD <-> CRR)
  * und externen Rechtsakten
  unterscheiden

Wichtige Abgrenzung:
- Mehrfachverweise wie "Articles 74 and 75" oder "Articles 32 to 35"
  werden hier bewusst noch nicht behandelt.
"""

import re


def _normalisiere_textfragment(textfragment):
    """Entfernt Zeilenumbrueche und doppelte Leerzeichen fuer besser lesbare Ausgabe."""

    return " ".join(textfragment.split())


def _text_nach_treffer(text, match_end, paraend, max_len=160):
    """Liest ein kurzes Textfenster direkt nach dem gefundenen Artikelverweis aus."""

    return text[match_end:min(match_end + max_len, paraend)]


def _text_vor_treffer(text, match_start, max_len=260):
    """Liest ein kurzes Textfenster direkt vor dem gefundenen Artikelverweis aus."""

    return text[max(0, match_start - max_len):match_start]


def _baue_externen_treffer(text, match_start, paraend, max_len=120):
    """Baut fuer externe Verweise einen lesbaren Treffertext.

    Fuer externe Verweise ist die nackte Artikelnummer meist nicht aussagekraeftig
    genug. Deshalb wird ein etwas laengeres Textfragment zurueckgegeben.
    """

    fragment = text[match_start:min(match_start + max_len, paraend)]
    return _normalisiere_textfragment(fragment)


def _ist_expliziter_crr_verweis(context_after_lower):
    """Prueft auf explizite Verweise von der CRD auf die CRR."""

    return "575/2013" in context_after_lower and "regulation" in context_after_lower


def _ist_expliziter_crd_verweis(context_after_lower):
    """Prueft auf explizite Verweise von der CRR auf die CRD."""

    return "2013/36/eu" in context_after_lower and "directive" in context_after_lower


def _ist_expliziter_selbstverweis(context_after_lower, current_act):
    """Prueft auf explizite Verweise auf den Eigenrechtsakt.

    Beispiele:
    - im CRD:  "Article X of Directive 2013/36/EU"
    - im CRR:  "Article X of Regulation (EU) No 575/2013"
    """

    if current_act == "CRD":
        return "2013/36/eu" in context_after_lower and "directive" in context_after_lower

    if current_act == "CRR":
        return "575/2013" in context_after_lower and "regulation" in context_after_lower

    return False


def _ist_expliziter_verweis_auf_denselben_rechtsakt(context_after_lower, current_act):
    """Prueft auf 'of this Directive' bzw. 'of this Regulation'."""

    context_after_clean = context_after_lower.lstrip()

    if current_act == "CRD":
        return context_after_clean.startswith("of this directive")

    if current_act == "CRR":
        return context_after_clean.startswith("of this regulation")

    return False


def _klassifiziere_that_verweis(context_before_lower, context_after_lower, current_act):
    """Ordnet 'of that Regulation' bzw. 'of that Directive' anhand des Vorkontexts zu.

    Rueckgabewerte:
    - "gleicher_rechtsakt"
    - "anderer_rechtsakt"
    - "extern"
    - None, wenn kein 'that'-Fall vorliegt oder keine sichere Zuordnung moeglich ist
    """

    context_after_clean = context_after_lower.lstrip()

    # Fall 1: "of that Regulation"
    if context_after_clean.startswith("of that regulation"):
        # Im CRD ist die relevante interne Regulation die CRR.
        if current_act == "CRD" and "575/2013" in context_before_lower and "regulation" in context_before_lower:
            return "anderer_rechtsakt"

        # Im CRR ist die relevante eigene Regulation die CRR selbst.
        if current_act == "CRR" and "575/2013" in context_before_lower and "regulation" in context_before_lower:
            return "gleicher_rechtsakt"

        # Sonstige Regulationen bleiben extern.
        if "regulation" in context_before_lower:
            return "extern"

    # Fall 2: "of that Directive"
    if context_after_clean.startswith("of that directive"):
        # Im CRD ist die relevante eigene Directive die CRD selbst.
        if current_act == "CRD" and "2013/36/eu" in context_before_lower and "directive" in context_before_lower:
            return "gleicher_rechtsakt"

        # Im CRR ist die relevante interne Directive die CRD.
        if current_act == "CRR" and "2013/36/eu" in context_before_lower and "directive" in context_before_lower:
            return "anderer_rechtsakt"

        # Sonstige Directives bleiben extern.
        if "directive" in context_before_lower:
            return "extern"

    return None


def _hat_externen_marker(context_after_lower):
    """Prueft auf klare Marker fuer externe Rechtsakte.

    Diese Funktion wird erst aufgerufen, nachdem moegliche CRD-/CRR-Gegenverweise
    bereits separat geprueft wurden.
    """

    context_after_clean = context_after_lower.lstrip()

    externe_marker = [
        "of regulation",
        "of directive",
        "of decision",
        "of delegated regulation",
        "of implementing regulation",
        "of that regulation",
        "of that directive",
    ]

    for marker in externe_marker:
        if context_after_clean.startswith(marker):
            return True

    return False


def _fuege_internen_verweis_hinzu(
    ziel,
    Verweise_Berechnung,
    Verweise_gleicher_Rechtsakt,
    Verweise_anderer_Rechtsakt,
    Verweise_gesamt,
    gleicher_rechtsakt,
):
    """Fuegt einen internen Verweis konsistent in die passenden Listen ein."""

    Verweise_Berechnung.append(ziel)
    Verweise_gesamt.append(ziel)

    if gleicher_rechtsakt:
        Verweise_gleicher_Rechtsakt.append(ziel)
    else:
        Verweise_anderer_Rechtsakt.append(ziel)


def einzelverweise_crd(
    text,
    parabegin,
    paraend,
    current_article,
    current_act,
    ParagraphList_CRD,
    ParagraphList_CRR,
):
    """Erkennt Einzelverweise im aktuellen Artikel.

    Rueckgabe:
    1. Verweise_Berechnung
       Alle internen Verweise im System CRD + CRR.
    2. Verweise_gleicher_Rechtsakt
       Verweise auf den gleichen Rechtsakt.
    3. Verweise_anderer_Rechtsakt
       Verweise auf den jeweils anderen internen Rechtsakt.
    4. Verweise_extern
       Externe Verweise als lesbare Textfragmente.
    5. Verweise_gesamt
       Alle erkannten Einzelverweise des aktuellen Artikels.
    """

    if current_act not in ("CRD", "CRR"):
        raise ValueError("current_act muss 'CRD' oder 'CRR' sein.")

    # Ergebnislisten
    Verweise_Berechnung = []
    Verweise_gleicher_Rechtsakt = []
    Verweise_anderer_Rechtsakt = []
    Verweise_extern = []
    Verweise_gesamt = []

    # Einzelverweise auf Artikelebene.
    # Erfasst z. B.:
    # - Article 30
    # - Article 30(2)
    # - Article 30(2)(a)
    #
    # In Group(1) landet immer nur die reine Artikelnummer.
    pattern = r"\bArticle\s+(\d+)(?:\([^)]+\))*"

    # Es wird nur der aktuelle Artikelbereich durchsucht.
    artikeltext = text[parabegin:paraend]

    for match in re.finditer(pattern, artikeltext):
        verweis_nummer = match.group(1)
        match_start = parabegin + match.start()
        match_end = parabegin + match.end()

        context_after = _text_nach_treffer(text, match_end, paraend)
        context_after_lower = context_after.lower()
        context_before = _text_vor_treffer(text, match_start)
        context_before_lower = context_before.lower()

        # 1. Expliziter Rechtsaktwechsel: CRD -> CRR
        if current_act == "CRD" and _ist_expliziter_crr_verweis(context_after_lower):
            if verweis_nummer in ParagraphList_CRR:
                ziel = "CRR_" + verweis_nummer
                _fuege_internen_verweis_hinzu(
                    ziel,
                    Verweise_Berechnung,
                    Verweise_gleicher_Rechtsakt,
                    Verweise_anderer_Rechtsakt,
                    Verweise_gesamt,
                    gleicher_rechtsakt=False,
                )
            continue

        # 2. Expliziter Rechtsaktwechsel: CRR -> CRD
        if current_act == "CRR" and _ist_expliziter_crd_verweis(context_after_lower):
            if verweis_nummer in ParagraphList_CRD:
                ziel = "CRD_" + verweis_nummer
                _fuege_internen_verweis_hinzu(
                    ziel,
                    Verweise_Berechnung,
                    Verweise_gleicher_Rechtsakt,
                    Verweise_anderer_Rechtsakt,
                    Verweise_gesamt,
                    gleicher_rechtsakt=False,
                )
            continue

        # 3. Expliziter Verweis auf denselben Rechtsakt durch ausgeschriebenen Eigenrechtsakt
        if _ist_expliziter_selbstverweis(context_after_lower, current_act):
            if current_act == "CRD":
                if verweis_nummer == current_article:
                    continue
                if verweis_nummer in ParagraphList_CRD:
                    ziel = "CRD_" + verweis_nummer
                    _fuege_internen_verweis_hinzu(
                        ziel,
                        Verweise_Berechnung,
                        Verweise_gleicher_Rechtsakt,
                        Verweise_anderer_Rechtsakt,
                        Verweise_gesamt,
                        gleicher_rechtsakt=True,
                    )
            else:
                if verweis_nummer == current_article:
                    continue
                if verweis_nummer in ParagraphList_CRR:
                    ziel = "CRR_" + verweis_nummer
                    _fuege_internen_verweis_hinzu(
                        ziel,
                        Verweise_Berechnung,
                        Verweise_gleicher_Rechtsakt,
                        Verweise_anderer_Rechtsakt,
                        Verweise_gesamt,
                        gleicher_rechtsakt=True,
                    )
            continue

        # 4. Expliziter Verweis auf denselben Rechtsakt
        if _ist_expliziter_verweis_auf_denselben_rechtsakt(context_after_lower, current_act):
            if current_act == "CRD":
                if verweis_nummer == current_article:
                    continue
                if verweis_nummer in ParagraphList_CRD:
                    ziel = "CRD_" + verweis_nummer
                    _fuege_internen_verweis_hinzu(
                        ziel,
                        Verweise_Berechnung,
                        Verweise_gleicher_Rechtsakt,
                        Verweise_anderer_Rechtsakt,
                        Verweise_gesamt,
                        gleicher_rechtsakt=True,
                    )
            else:
                if verweis_nummer == current_article:
                    continue
                if verweis_nummer in ParagraphList_CRR:
                    ziel = "CRR_" + verweis_nummer
                    _fuege_internen_verweis_hinzu(
                        ziel,
                        Verweise_Berechnung,
                        Verweise_gleicher_Rechtsakt,
                        Verweise_anderer_Rechtsakt,
                        Verweise_gesamt,
                        gleicher_rechtsakt=True,
                    )
            continue

        # 5. 'of that Regulation' / 'of that Directive' mit einfacher Kontextzuordnung
        that_klassifikation = _klassifiziere_that_verweis(
            context_before_lower,
            context_after_lower,
            current_act,
        )

        if that_klassifikation == "gleicher_rechtsakt":
            if current_act == "CRD":
                if verweis_nummer == current_article:
                    continue
                if verweis_nummer in ParagraphList_CRD:
                    ziel = "CRD_" + verweis_nummer
                    _fuege_internen_verweis_hinzu(
                        ziel,
                        Verweise_Berechnung,
                        Verweise_gleicher_Rechtsakt,
                        Verweise_anderer_Rechtsakt,
                        Verweise_gesamt,
                        gleicher_rechtsakt=True,
                    )
            else:
                if verweis_nummer == current_article:
                    continue
                if verweis_nummer in ParagraphList_CRR:
                    ziel = "CRR_" + verweis_nummer
                    _fuege_internen_verweis_hinzu(
                        ziel,
                        Verweise_Berechnung,
                        Verweise_gleicher_Rechtsakt,
                        Verweise_anderer_Rechtsakt,
                        Verweise_gesamt,
                        gleicher_rechtsakt=True,
                    )
            continue

        if that_klassifikation == "anderer_rechtsakt":
            if current_act == "CRD":
                if verweis_nummer in ParagraphList_CRR:
                    ziel = "CRR_" + verweis_nummer
                    _fuege_internen_verweis_hinzu(
                        ziel,
                        Verweise_Berechnung,
                        Verweise_gleicher_Rechtsakt,
                        Verweise_anderer_Rechtsakt,
                        Verweise_gesamt,
                        gleicher_rechtsakt=False,
                    )
            else:
                if verweis_nummer in ParagraphList_CRD:
                    ziel = "CRD_" + verweis_nummer
                    _fuege_internen_verweis_hinzu(
                        ziel,
                        Verweise_Berechnung,
                        Verweise_gleicher_Rechtsakt,
                        Verweise_anderer_Rechtsakt,
                        Verweise_gesamt,
                        gleicher_rechtsakt=False,
                    )
            continue

        if that_klassifikation == "extern":
            externer_treffer = _baue_externen_treffer(text, match_start, paraend)
            Verweise_extern.append(externer_treffer)
            Verweise_gesamt.append(externer_treffer)
            continue

        # 6. Klar externer Verweis auf einen anderen Rechtsakt
        if _hat_externen_marker(context_after_lower):
            externer_treffer = _baue_externen_treffer(text, match_start, paraend)
            Verweise_extern.append(externer_treffer)
            Verweise_gesamt.append(externer_treffer)
            continue

        # 7. Standardfall ohne Marker:
        # "Article X" wird als interner Verweis im aktuellen Rechtsakt behandelt.
        if current_act == "CRD":
            if verweis_nummer == current_article:
                continue
            if verweis_nummer in ParagraphList_CRD:
                ziel = "CRD_" + verweis_nummer
                _fuege_internen_verweis_hinzu(
                    ziel,
                    Verweise_Berechnung,
                    Verweise_gleicher_Rechtsakt,
                    Verweise_anderer_Rechtsakt,
                    Verweise_gesamt,
                    gleicher_rechtsakt=True,
                )
            continue

        if current_act == "CRR":
            if verweis_nummer == current_article:
                continue
            if verweis_nummer in ParagraphList_CRR:
                ziel = "CRR_" + verweis_nummer
                _fuege_internen_verweis_hinzu(
                    ziel,
                    Verweise_Berechnung,
                    Verweise_gleicher_Rechtsakt,
                    Verweise_anderer_Rechtsakt,
                    Verweise_gesamt,
                    gleicher_rechtsakt=True,
                )
            continue

    return (
        Verweise_Berechnung,
        Verweise_gleicher_Rechtsakt,
        Verweise_anderer_Rechtsakt,
        Verweise_extern,
        Verweise_gesamt,
    )
