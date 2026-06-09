'''Version: 09.06.2026
Funktion zur Identifizierung von Mehrfachverweisen im CRD-Text.

Diese Datei ist bewusst einfach aufgebaut.
Sie behandelt nur Artikelverweise im Plural, also z.B.:
- Articles 10 to 14
- Articles 74 and 75
- Articles 22, 25 and 26

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
    """Schneidet Rechtsaktangaben ab, damit 575/2013 nicht als Artikel gelesen wird."""

    match = re.search(r"\s+of\s+(?:that\s+)?(?:regulation|directive|decision)\b", fragment, re.IGNORECASE)

    if match is not None:
        fragment = fragment[:match.start()]

    # Stoppt vor einem spaeteren Singularverweis, z.B.:
    # Articles 283 and 363, and ... Article 259(3)
    singular_match = re.search(r"\bArticle\s+\d+", fragment[len("Articles"):], re.IGNORECASE)
    if singular_match is not None:
        fragment = fragment[:len("Articles") + singular_match.start()]

    return fragment


def extrahiere_artikelnummern(fragment, ParagraphList):
    """Extrahiert Artikelnummern aus einem Mehrfachverweisfragment."""

    verweise = []
    fragment = artikelteil_ohne_rechtsaktnummern(fragment)

    # Erkennt Bereichsverweise wie "Articles 10 to 14".
    for match in re.finditer(r"\b(\d+)(?:\([^)]+\))*\s+to\s*(\d+)(?:\([^)]+\))*", fragment):
        verweise += baue_bereich(match.group(1), match.group(2), ParagraphList)

    # Erkennt Bereichsverweise wie "Articles 10 through 14".
    for match in re.finditer(r"\b(\d+)(?:\([^)]+\))*\s+through\s*(\d+)(?:\([^)]+\))*", fragment):
        verweise += baue_bereich(match.group(1), match.group(2), ParagraphList)

    # Entfernt bereits behandelte Bereichsverweise, damit die Grenzen nicht doppelt gezaehlt werden.
    fragment_ohne_bereiche = re.sub(r"\b\d+(?:\([^)]+\))*\s+(?:to|through)\s*\d+(?:\([^)]+\))*", " ", fragment)

    # Erkennt einzelne Zahlen in Aufzaehlungen wie "Articles 22, 25 and 26".
    for match in re.finditer(r"(?<!\()\b\d+(?:\([^)]+\))*", fragment_ohne_bereiche):
        verweise.append(match.group(0).split("(")[0])

    return eindeutige_liste(verweise)


def ziel_ist_crr(fragment):
    """Prueft, ob der Mehrfachverweis auf Regulation (EU) No 575/2013 zeigt."""

    fragment_norm = normalisiere_kontext(fragment)
    return "575/2013" in fragment_norm and "regulation" in fragment_norm


def ziel_ist_extern(fragment):
    """Prueft, ob der Mehrfachverweis auf einen anderen Rechtsakt zeigt."""

    fragment_norm = normalisiere_kontext(fragment)

    if ziel_ist_crr(fragment):
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


def mehrfachverweise_crd(parabegin, paraend, counter_multi_ref,
                         counter_non_identified_ref, counter_non_identified_ref2,
                         CFR_Text, ParagraphList=None, current_paragraph=None):
    """Sucht Mehrfachverweise im aktuellen CRD-Artikel."""

    Mehrfachverweise = []
    ExterneMehrfachverweise = []
    CRRMehrfachverweise = []

    if ParagraphList is None:
        ParagraphList = []

    # Sucht nur Pluralformen wie "Articles 10 to 14".
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
        artikelnummern = extrahiere_artikelnummern(fragment, ParagraphList)

        if len(artikelnummern) == 0:
            counter_non_identified_ref += 1
            continue

        if ziel_ist_crr(fragment):
            CRRMehrfachverweise += artikelnummern
            continue

        if ziel_ist_extern(fragment):
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
        eindeutige_liste(CRRMehrfachverweise),
        counter_multi_ref,
        counter_non_identified_ref,
        counter_non_identified_ref2,
    )
