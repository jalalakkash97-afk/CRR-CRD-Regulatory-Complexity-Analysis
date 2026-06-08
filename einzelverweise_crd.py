"""Version: 08.06.2026
Einfacher Umbau der Einzelverweiserkennung fuer CRD- und CRR-Texte.

Die Datei verfolgt jetzt einen moeglichst einfachen Aufbau:
1. Einzelverweis im aktuellen Artikel finden
2. auf Artikelebene reduzieren
3. Ziel als
   - gleicher Rechtsakt,
   - anderer interner Rechtsakt,
   - extern
   einordnen
4. passende Listen zurueckgeben

Wichtige Abgrenzung:
- Nur Einzelverweise werden hier behandelt.
- Mehrfachverweise wie "Articles 74 and 75" oder "Articles 32 to 35"
  gehoeren spaeter in mehrfachverweise.py.
"""

import re


def text_nach_verweis(text, match_end, paraend):
    """Liest ein kurzes Textfenster direkt nach dem gefundenen Verweis aus."""

    return text[match_end:min(match_end + 160, paraend)]


def text_vor_verweis(text, match_start):
    """Liest ein kurzes Textfenster direkt vor dem gefundenen Verweis aus."""

    return text[max(0, match_start - 260):match_start]


def externen_treffer_bauen(text, match_start, paraend):
    """Baut fuer externe Verweise ein lesbares Textfragment."""

    fragment = text[match_start:min(match_start + 120, paraend)]
    return " ".join(fragment.split())


def unique_list(values):
    """Entfernt doppelte Eintraege, behaelt aber die erste Fundreihenfolge bei."""

    values_clean = []
    for value in values:
        if value not in values_clean:
            values_clean.append(value)
    return values_clean


def expliziter_crr_verweis(context_after_lower):
    """Prueft auf Verweise auf Regulation (EU) No 575/2013."""

    return "575/2013" in context_after_lower and "regulation" in context_after_lower


def expliziter_crd_verweis(context_after_lower):
    """Prueft auf Verweise auf Directive 2013/36/EU."""

    return "2013/36/eu" in context_after_lower and "directive" in context_after_lower


def expliziter_selbstverweis(context_after_lower, current_act):
    """Prueft auf ausgeschriebene Verweise auf den eigenen Rechtsakt."""

    if current_act == "CRD":
        return expliziter_crd_verweis(context_after_lower)

    if current_act == "CRR":
        return expliziter_crr_verweis(context_after_lower)

    return False


def verweis_auf_denselben_rechtsakt(context_after_lower, current_act):
    """Prueft auf 'of this Directive' bzw. 'of this Regulation'."""

    context_after_clean = context_after_lower.lstrip()

    if current_act == "CRD":
        return context_after_clean.startswith("of this directive")

    if current_act == "CRR":
        return context_after_clean.startswith("of this regulation")

    return False


def klassifiziere_that_verweis(context_before_lower, context_after_lower):
    """Ordnet 'of that Regulation' oder 'of that Directive' einem Zielrechtsakt zu.

    Rueckgabe:
    - "CRD"
    - "CRR"
    - "EXTERN"
    - None
    """

    context_after_clean = context_after_lower.lstrip()

    if context_after_clean.startswith("of that regulation"):
        if "575/2013" in context_before_lower and "regulation" in context_before_lower:
            return "CRR"
        if "regulation" in context_before_lower:
            return "EXTERN"

    if context_after_clean.startswith("of that directive"):
        if "2013/36/eu" in context_before_lower and "directive" in context_before_lower:
            return "CRD"
        if "directive" in context_before_lower:
            return "EXTERN"

    return None


def hat_externen_marker(context_after_lower):
    """Prueft auf klare Marker fuer externe Rechtsakte."""

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


def internen_verweis_hinzufuegen(
    ziel,
    current_act,
    Verweise_Berechnung,
    Verweise_gleicher_Rechtsakt,
    Verweise_anderer_Rechtsakt,
    Verweise_gesamt,
):
    """Fuegt einen internen Verweis in die passenden Listen ein."""

    Verweise_Berechnung.append(ziel)
    Verweise_gesamt.append(ziel)

    if ziel.startswith(current_act + "_"):
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
    """Erkennt Einzelverweise fuer genau einen Artikel.

    Rueckgabe:
    1. Verweise_Berechnung
    2. Verweise_gleicher_Rechtsakt
    3. Verweise_anderer_Rechtsakt
    4. Verweise_extern
    5. Verweise_gesamt
    """

    if current_act not in ("CRD", "CRR"):
        raise ValueError("current_act muss 'CRD' oder 'CRR' sein.")

    Verweise_Berechnung = []
    Verweise_gleicher_Rechtsakt = []
    Verweise_anderer_Rechtsakt = []
    Verweise_extern = []
    Verweise_gesamt = []

    pattern = r"\bArticle\s+(\d+)(?:\([^)]+\))*"
    artikeltext = text[parabegin:paraend]

    for match in re.finditer(pattern, artikeltext):
        verweis_nummer = match.group(1)
        match_start = parabegin + match.start()
        match_end = parabegin + match.end()

        context_after = text_nach_verweis(text, match_end, paraend)
        context_before = text_vor_verweis(text, match_start)
        context_after_lower = context_after.lower()
        context_before_lower = context_before.lower()

        ziel_act = None
        externer_treffer = None

        # 1. Expliziter Wechsel CRD -> CRR
        if current_act == "CRD" and expliziter_crr_verweis(context_after_lower):
            ziel_act = "CRR"

        # 2. Expliziter Wechsel CRR -> CRD
        elif current_act == "CRR" and expliziter_crd_verweis(context_after_lower):
            ziel_act = "CRD"

        # 3. Ausgeschriebener Selbstverweis
        elif expliziter_selbstverweis(context_after_lower, current_act):
            ziel_act = current_act

        # 4. 'this Directive' / 'this Regulation'
        elif verweis_auf_denselben_rechtsakt(context_after_lower, current_act):
            ziel_act = current_act

        # 5. 'that Directive' / 'that Regulation'
        else:
            that_target = klassifiziere_that_verweis(context_before_lower, context_after_lower)
            if that_target == "EXTERN":
                externer_treffer = externen_treffer_bauen(text, match_start, paraend)
            elif that_target in ("CRD", "CRR"):
                ziel_act = that_target

        # 6. Sonstige klare externe Marker
        if ziel_act is None and externer_treffer is None and hat_externen_marker(context_after_lower):
            externer_treffer = externen_treffer_bauen(text, match_start, paraend)

        # 7. Standardfall ohne Marker: interner Verweis im aktuellen Rechtsakt
        if ziel_act is None and externer_treffer is None:
            ziel_act = current_act

        # 8. Externe Verweise speichern
        if externer_treffer is not None:
            Verweise_extern.append(externer_treffer)
            Verweise_gesamt.append(externer_treffer)
            continue

        # 9. Zielknoten bilden und gegen die Artikellisten pruefen
        if ziel_act == "CRD":
            if verweis_nummer == current_article and current_act == "CRD":
                continue
            if verweis_nummer not in ParagraphList_CRD:
                continue
            ziel = "CRD_" + verweis_nummer
            internen_verweis_hinzufuegen(
                ziel,
                current_act,
                Verweise_Berechnung,
                Verweise_gleicher_Rechtsakt,
                Verweise_anderer_Rechtsakt,
                Verweise_gesamt,
            )
            continue

        if ziel_act == "CRR":
            if verweis_nummer == current_article and current_act == "CRR":
                continue
            if verweis_nummer not in ParagraphList_CRR:
                continue
            ziel = "CRR_" + verweis_nummer
            internen_verweis_hinzufuegen(
                ziel,
                current_act,
                Verweise_Berechnung,
                Verweise_gleicher_Rechtsakt,
                Verweise_anderer_Rechtsakt,
                Verweise_gesamt,
            )
            continue

    return (
        unique_list(Verweise_Berechnung),
        unique_list(Verweise_gleicher_Rechtsakt),
        unique_list(Verweise_anderer_Rechtsakt),
        unique_list(Verweise_extern),
        unique_list(Verweise_gesamt),
    )


def sammle_einzelverweise_fuer_rechtsakt(
    text,
    positions_paragraph,
    end_paragraph,
    paragraph_list,
    current_act,
    ParagraphList_CRD,
    ParagraphList_CRR,
):
    """Uebergangshilfe fuer den aktuellen main.py.

    Fachlich gehoert der Kern weiter in einzelverweise_crd(...).
    Diese Funktion sammelt nur die Rueckgaben fuer alle Artikel eines Rechtsakts.
    """

    verweise_berechnung_alle = []
    verweise_gleicher_rechtsakt_alle = []
    verweise_anderer_rechtsakt_alle = []
    verweise_extern_alle = []
    verweise_gesamt_alle = []

    for counter in range(len(positions_paragraph)):
        parabegin = positions_paragraph[counter]
        paraend = end_paragraph[counter]
        current_article = paragraph_list[counter]

        (
            Verweise_Berechnung,
            Verweise_gleicher_Rechtsakt,
            Verweise_anderer_Rechtsakt,
            Verweise_extern,
            Verweise_gesamt,
        ) = einzelverweise_crd(
            text,
            parabegin,
            paraend,
            current_article,
            current_act,
            ParagraphList_CRD,
            ParagraphList_CRR,
        )

        verweise_berechnung_alle.append(Verweise_Berechnung)
        verweise_gleicher_rechtsakt_alle.append(Verweise_gleicher_Rechtsakt)
        verweise_anderer_rechtsakt_alle.append(Verweise_anderer_Rechtsakt)
        verweise_extern_alle.append(Verweise_extern)
        verweise_gesamt_alle.append(Verweise_gesamt)

    return (
        verweise_berechnung_alle,
        verweise_gleicher_rechtsakt_alle,
        verweise_anderer_rechtsakt_alle,
        verweise_extern_alle,
        verweise_gesamt_alle,
    )
