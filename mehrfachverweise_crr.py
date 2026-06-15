'''Version: 09.06.2026
Funktion zur Identifizierung von Mehrfachverweisen im CRR-Text.

Diese Datei ist analog zu mehrfachverweise_crd.py aufgebaut.
Sie behandelt nur Artikelverweise im Plural, also z.B.:
- Articles 32 to 35
- Articles 89, 90 and 91
- Articles 405 or 406

Chapter-, Title- und Annex-Verweise werden hier nicht ausgewertet.
'''

import re


def normalisiere_kontext(text):
    """Vereinheitlicht kurze Textausschnitte fuer stabilere Mustererkennung."""

    text = text.replace("\n", " ")
    text = re.sub(r"/\s+", "/", text)
    text = " ".join(text.split())
    return text.lower()


def eindeutige_liste(werte):
    """Entfernt Dopplungen und behaelt die Fundreihenfolge bei."""

    ergebnis = []
    for wert in werte:
        if wert not in ergebnis:
            ergebnis.append(wert)
    return ergebnis


def baue_bereich(start, ende, ParagraphList):
    """Baut aus Articles X to Y eine Liste aller vorhandenen Artikel zwischen X und Y."""

    if start not in ParagraphList or ende not in ParagraphList:
        return []

    start_index = ParagraphList.index(start)
    ende_index = ParagraphList.index(ende)

    if start_index > ende_index:
        return []

    return ParagraphList[start_index:ende_index + 1]


def artikelteil_ohne_rechtsaktnummern(fragment):
    """Schneidet Rechtsaktangaben ab, damit 1093/2010 nicht als Artikel gelesen wird."""

    match = re.search(r"\s+of\s+(?:that\s+)?(?:regulation|directive|decision)\b", fragment, re.IGNORECASE)

    if match is not None:
        fragment = fragment[:match.start()]

    # Stoppt vor einem spaeteren Singularverweis, damit Einzelverweise getrennt bleiben.
    follow_up_match = re.search(r"\bArticles?\s+\d+[a-z]?", fragment[len("Articles"):], re.IGNORECASE)
    if follow_up_match is not None:
        fragment = fragment[:len("Articles") + follow_up_match.start()]

    return fragment


def relevanter_mehrfachverweis_text(fragment):
    """Grenzt den Text auf den eigentlichen Mehrfachverweis ein."""

    # Stoppt vor einem spaeteren Singularverweis, damit dessen Rechtsaktangabe
    # nicht faelschlich auf den vorherigen Mehrfachverweis uebertragen wird.
    follow_up_match = re.search(r"\bArticles?\s+\d+[a-z]?", fragment[len("Articles"):], re.IGNORECASE)
    if follow_up_match is not None:
        fragment = fragment[:len("Articles") + follow_up_match.start()]

    return fragment


def extrahiere_artikelnummern(fragment, ParagraphList):
    """Extrahiert Artikelnummern aus einem Mehrfachverweisfragment."""

    verweise = []
    fragment = artikelteil_ohne_rechtsaktnummern(fragment)

    # Erkennt Bereichsverweise wie "Articles 32 to 35".
    for match in re.finditer(r"\b(\d+[a-z]?)(?:\([^)]+\))*\s+to\s*(\d+[a-z]?)(?:\([^)]+\))*", fragment, re.IGNORECASE):
        verweise += baue_bereich(match.group(1).lower(), match.group(2).lower(), ParagraphList)

    # Erkennt Bereichsverweise wie "Articles 32 through 35".
    for match in re.finditer(r"\b(\d+[a-z]?)(?:\([^)]+\))*\s+through\s*(\d+[a-z]?)(?:\([^)]+\))*", fragment, re.IGNORECASE):
        verweise += baue_bereich(match.group(1).lower(), match.group(2).lower(), ParagraphList)

    # Entfernt bereits behandelte Bereichsverweise, damit die Grenzen nicht doppelt gezaehlt werden.
    fragment_ohne_bereiche = re.sub(r"\b\d+[a-z]?(?:\([^)]+\))*\s+(?:to|through)\s*\d+[a-z]?(?:\([^)]+\))*", " ", fragment, flags=re.IGNORECASE)

    # Erkennt einzelne Zahlen in Aufzaehlungen wie "Articles 89, 90 and 91".
    for match in re.finditer(r"(?<!\()\b\d+[a-z]?(?:\([^)]+\))*", fragment_ohne_bereiche, re.IGNORECASE):
        verweise.append(match.group(0).split("(")[0].lower())

    return eindeutige_liste(verweise)


def ziel_ist_crd(fragment):
    """Prueft, ob der Mehrfachverweis auf Directive 2013/36/EU zeigt."""

    fragment_norm = normalisiere_kontext(fragment)
    fragment_compact = fragment_norm.replace(" ", "")
    return "2013/36/eu" in fragment_compact and "directive" in fragment_norm


def ziel_ist_extern(fragment):
    """Prueft, ob der Mehrfachverweis auf einen anderen Rechtsakt zeigt."""

    fragment_norm = normalisiere_kontext(fragment)

    if ziel_ist_crd(fragment):
        return False

    externe_marker = [
        "of regulation",
        "of directive",
        "of decision",
        "of that regulation",
        "of that directive",
    ]

    for marker in externe_marker:
        if marker in fragment_norm:
            return True

    return False


def mehrfachverweise_crr(parabegin, paraend, counter_multi_ref,
                         counter_non_identified_ref, counter_non_identified_ref2,
                         CFR_Text, ParagraphList=None, current_paragraph=None):
    """Sucht Mehrfachverweise im aktuellen CRR-Artikel."""

    Mehrfachverweise = []
    ExterneMehrfachverweise = []
    CRDMehrfachverweise = []

    if ParagraphList is None:
        ParagraphList = []

    # Sucht nur Pluralformen wie "Articles 32 to 35".
    pattern = r"\bArticles\s+"

    for match in re.finditer(pattern, CFR_Text[parabegin:paraend]):
        counter_multi_ref += 1

        match_start = parabegin + match.start()

        # Das Fragment laeuft bis zum naechsten Punkt oder Semikolon.
        fragment_end = paraend
        for marker in [".", ";"]:
            marker_pos = CFR_Text.find(marker, match_start, paraend)
            if marker_pos != -1:
                fragment_end = min(fragment_end, marker_pos)

        fragment = CFR_Text[match_start:fragment_end]
        relevanter_text = relevanter_mehrfachverweis_text(fragment)
        artikelnummern = extrahiere_artikelnummern(relevanter_text, ParagraphList)

        if len(artikelnummern) == 0:
            counter_non_identified_ref += 1
            continue

        if ziel_ist_crd(relevanter_text):
            CRDMehrfachverweise += artikelnummern
            continue

        if ziel_ist_extern(relevanter_text):
            ExterneMehrfachverweise += artikelnummern
            continue

        for verweis in artikelnummern:
            if verweis == current_paragraph:
                continue
            if verweis in ParagraphList:
                Mehrfachverweise.append(verweis)

    return (
        eindeutige_liste(Mehrfachverweise),
        eindeutige_liste(ExterneMehrfachverweise),
        eindeutige_liste(CRDMehrfachverweise),
        counter_multi_ref,
        counter_non_identified_ref,
        counter_non_identified_ref2,
    )
