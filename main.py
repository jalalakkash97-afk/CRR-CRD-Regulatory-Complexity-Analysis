
import numpy as np
from functools import cmp_to_key
import copy

from einzelverweise import einzelverweise
from einzelverweise_crd import einzelverweise_crd
from paragraph_begin_end import paragraphenbeginend
from mehrfachverweise import mehrfachverweise
from index_verweis import index_verweise

from load_operators import load_operators
from load_text import load_text
from reference_corrections import reference_corrections
from operator_counting import operator_counting
from computing_fres import computing_fres
from factors import verweis_factor_fun
from factors import zirkel_factor_fun
from contraction import zirkelkontraktion
from compute_complexity import compute_complexity
from clumb_analysis import clumb_analysis
from compute_statistics import compute_statistics
from write_output import write_output



###### Laden der Operatoren ##############
(reg_operators,log_operators,math_operators) = load_operators()



#######################################################################################################################
for year in range(2013, 2014):
    # Pfad zur CRD-Datei fuer das betrachtete Jahr.
    crd_file_name = "C:/Users/jalal/OneDrive/Desktop/MASTERARBEIT/Texte/txt/CELEX_32013L0036_EN_TXT.txt"
    # Pfad zur CRR-Datei fuer dasselbe Jahr.
    crr_file_name = f"C:/Users/jalal/OneDrive/Desktop/MASTERARBEIT/Texte/CRR_Texte/CRR_{year}.txt"

    # Kontrollausgabe: zeigt, welche CRD-Datei geladen werden soll.
    print("CRD-Datei:", crd_file_name)
    # Kontrollausgabe: zeigt, welche CRR-Datei geladen werden soll.
    print("CRR-Datei:", crr_file_name)

    # Liest den kompletten CRD-Text als String ein.
    CRD_Text = load_text(crd_file_name)
    # Liest den kompletten CRR-Text als String ein.
    CRR_Text = load_text(crr_file_name)

    # Kontrollausgabe zur Plausibilitaet: Laenge des eingelesenen CRD-Texts.
    print("CRD-Textlaenge:", len(CRD_Text))
    # Kontrollausgabe zur Plausibilitaet: Laenge des eingelesenen CRR-Texts.
    print("CRR-Textlaenge:", len(CRR_Text))

    # Zwischenschritt:
    # Der restliche Code arbeitet vorerst noch mit dem bisherigen Variablennamen.
    # Bis die nachfolgenden Bloecke ebenfalls umgestellt sind, bleibt CFR_Text daher
    # bewusst auf den CRD-Text gesetzt.
    CFR_Text = CRD_Text
    #print("Textlänge:", len(CFR_Text))
    #print("Erste 300 Zeichen:\n")
    #print(CFR_Text[:300])

    #input("STOP – Datei wurde geladen")
    #exit ()
    
    ##################################################################
    ################# 2) Paragraphenfänge bestimmen ##################
    ##################################################################


    # Importiert regulaere Ausdruecke; damit koennen Artikelueberschriften per Muster erkannt werden.
    import re

    # Hilfsfunktion zur Erkennung aller Artikel in einem EU-Rechtstext.
    # Die Funktion arbeitet sowohl fuer den CRD- als auch fuer den CRR-Text.
    def erkenne_artikel_im_eu_text(text):
        # Speichert die Startposition jedes gefundenen Artikels im Gesamttext.
        positions = []
        # Speichert die Endposition jedes gefundenen Artikels im Gesamttext.
        ends = []
        # Speichert die Artikelnummern als Namen der Knoten, z.B. "1", "2", "3".
        artikel_liste = []

        # Echte Artikelüberschriften erkennen, z.B.:
        # "\nArticle 1\n"
        # "\n Article 1\n"
        # "\n   Article 1\n"
        # Das Muster sucht daher:
        # - einen Zeilenumbruch,
        # - optional bis zu drei Leerzeichen,
        # - das Wort "Article",
        # - mindestens ein Leerzeichen,
        # - eine oder mehrere Ziffern als Artikelnummer,
        # - und danach wieder einen Zeilenumbruch.
        pattern = r"\n[ ]{0,3}Article\s+(\d+)\n"
        # Sucht alle passenden Artikelueberschriften im uebergebenen Text.
        matches = list(re.finditer(pattern, text))

        # Geht alle gefundenen Artikelueberschriften nacheinander durch.
        for i in range(len(matches)):
            # Speichert die Artikelnummer des aktuellen Treffers.
            artikel_liste.append(matches[i].group(1))    # Gruppe 1 ist der Inhalt der ersten Kammer im Pattern 
            # Speichert die Startposition des aktuellen Artikels.
            artikelfang = matches[i].start()

            # Wenn noch ein weiterer Artikel folgt, endet der aktuelle Artikel direkt vor dem naechsten.
            if i < len(matches) - 1:
                artikelende = matches[i + 1].start()
            else:
                # Letzten Artikel vor Anhängen oder Schlussformeln begrenzen.
                # Diese Marker liegen typischerweise nach dem eigentlichen Rechtstext.
                possible_ends = []
                # Prueft mehrere moegliche Endmarker, damit die Logik sowohl bei CRD als auch bei CRR robust bleibt.
                for marker in ["\nANNEX I", "\nANNEX", "\nDone at Brussels"]:
                    # Sucht den Marker erst ab dem Beginn des letzten Artikels.
                    pos = text.find(marker, artikelfang)
                    # Nur Treffer hinter dem Artikelanfang sind als Artikelende relevant.
                    if pos != -1 and pos > artikelfang:
                        # Speichert alle gueltigen Endkandidaten.
                        possible_ends.append(pos)

                # Wenn ein Endmarker gefunden wurde, wird der frueheste davon als Artikelende verwendet.
                if len(possible_ends) > 0:
                    artikelende = min(possible_ends)
                else:
                    # Falls kein Endmarker gefunden wird, laeuft der letzte Artikel bis zum Textende.
                    artikelende = len(text)

            # Fuegt die Startposition des aktuellen Artikels der Positionsliste hinzu.
            positions.append(artikelfang)
            # Fuegt die Endposition des aktuellen Artikels der Endliste hinzu.
            ends.append(artikelende)

        # Gibt fuer den uebergebenen Text alle Startpositionen, Endpositionen und Artikelnamen zurueck.
        return positions, ends, artikel_liste

    # Erkennt alle Artikel im CRD-Text und speichert Positionen, Enden und Artikelnamen getrennt.
    PositionsParagraph_CRD, EndParagraph_CRD, ParagraphList_CRD = erkenne_artikel_im_eu_text(CRD_Text)
    # Erkennt alle Artikel im CRR-Text und speichert Positionen, Enden und Artikelnamen getrennt.
    PositionsParagraph_CRR, EndParagraph_CRR, ParagraphList_CRR = erkenne_artikel_im_eu_text(CRR_Text)

    # Kontrollausgabe: Anzahl der im CRD gefundenen Artikel.
    print("CRD-Artikel:", len(ParagraphList_CRD))
    # Kontrollausgabe: Anzahl der im CRR gefundenen Artikel.
    print("CRR-Artikel:", len(ParagraphList_CRR))

    # Detailliertere Kontrollausgabe zur Plausibilitaet der Artikelerkennung im CRD.
    if len(ParagraphList_CRD) > 0:
        print("CRD erster Artikel:", ParagraphList_CRD[0], "| letzter Artikel:", ParagraphList_CRD[-1])
    else:
        print("CRD: Keine Artikel erkannt.")

    # Detailliertere Kontrollausgabe zur Plausibilitaet der Artikelerkennung im CRR.
    if len(ParagraphList_CRR) > 0:
        print("CRR erster Artikel:", ParagraphList_CRR[0], "| letzter Artikel:", ParagraphList_CRR[-1])
    else:
        print("CRR: Keine Artikel erkannt.")

    # Baut fuer die CRD eindeutige interne Knotennamen auf.
    # Beispiel: Aus Artikel "4" wird der interne Name "CRD_4".
    ParagraphList_CRD_Internal = ["CRD_" + artikel for artikel in ParagraphList_CRD]

    # Baut fuer die CRR ebenfalls eindeutige interne Knotennamen auf.
    # Beispiel: Aus Artikel "4" wird der interne Name "CRR_4".
    ParagraphList_CRR_Internal = ["CRR_" + artikel for artikel in ParagraphList_CRR]

    # Erzeugt die gemeinsame interne Artikelliste fuer das Gesamtsystem aus CRD und CRR.
    # Diese Liste soll spaeter die Grundlage fuer die Berechnung bilden, damit Verweise
    # zwischen beiden Rechtsakten als interne Verweise behandelt werden koennen.
    ParagraphList_All = ParagraphList_CRD_Internal + ParagraphList_CRR_Internal

    # Kontrollausgabe: Anzahl aller internen Knoten im gemeinsamen CRD/CRR-System.
    print("Interne Artikel gesamt (CRD + CRR):", len(ParagraphList_All))

    # Zusätzliche Plausibilitaetsausgabe: zeigt die ersten internen Knotennamen je Rechtsakt.
    if len(ParagraphList_CRD_Internal) > 0:
        print("Erster interner CRD-Knoten:", ParagraphList_CRD_Internal[0])
    if len(ParagraphList_CRR_Internal) > 0:
        print("Erster interner CRR-Knoten:", ParagraphList_CRR_Internal[0])

    # Zwischenschritt:
    # Die nachfolgende Verweislogik arbeitet vorerst noch mit den bisherigen Namen
    # und nur auf dem CRD-Text. Bis die Verweislogik ebenfalls umgestellt ist,
    # bleiben die Legacy-Variablen auf die CRD-Listen gesetzt.
    # Legacy-Name fuer die nachfolgende alte Verweislogik: aktuell noch nur die CRD-Artikel.
    PositionsParagraph = PositionsParagraph_CRD
    # Legacy-Endpositionen fuer die nachfolgende alte Verweislogik: aktuell noch nur die CRD-Artikel.
    EndParagraph = EndParagraph_CRD
    # Legacy-Artikelliste fuer die nachfolgende alte Verweislogik: aktuell noch nur die CRD-Artikel.
    ParagraphList = ParagraphList_CRD
 
    ##################################################################
    ################# 3) Verweise in jedem Paragraph identifizieren ##
    ##################################################################

    # Ergebnisliste fuer interne Artikelverweise.
    # Jede Position entspricht einem Artikel aus ParagraphList.
    ParagraphVerweise = []

    # Zusaetzliche Ergebnisliste fuer externe Artikelverweise.
    # Diese Liste wird nicht fuer die interne Komplexitaetsberechnung verwendet,
    # ist aber wichtig fuer spaetere Statistiken und Dokumentation.
    ParagraphExternalVerweise = []

    # Zusaetzliche Ergebnisliste fuer externe Artikelverweise auf die CRR.
    # Gemeint ist Regulation (EU) No 575/2013.
    ParagraphCRRVerweise = []

    # Diese Zaehler bleiben aus der Originalstruktur erhalten.
    # Fuer einfache Einzelverweise werden sie noch nicht gebraucht.
    counter_non_identified_ref = 0
    counter_multi_ref = 0
    counter_non_identified_ref2 = 0

    # Schreibweisen fuer einfache Einzelverweise.
    # In diesem ersten Schritt suchen wir nur nach Singularformen wie "Article 30".
    ParagraphSignArray = ["Article"]

    # Geht durch alle gefundenen Artikel.
    for counter in range(len(PositionsParagraph)):

        # Beginn des aktuellen Artikels.
        parabegin = PositionsParagraph[counter]

        # Ende des aktuellen Artikels.
        paraend = EndParagraph[counter]

        # Interne Verweise des aktuellen Artikels.
        Verweise = []

        # Externe Verweise des aktuellen Artikels.
        ExterneVerweise = []

        # CRR-Verweise des aktuellen Artikels.
        CRRVerweise = []

        # Geht durch alle Suchsignale fuer einfache Artikelverweise.
        for index_i in range(len(ParagraphSignArray)):

            # Aktuelles Suchsignal, hier erstmal nur "Article".
            ParagraphSign = ParagraphSignArray[index_i]

            # Sucht einfache Artikelverweise im aktuellen Artikel.
            # Die Funktion gibt interne und externe Verweise getrennt zurueck.
            verweise, externe_verweise, crr_verweise = einzelverweise_crd(
                ParagraphSign,
                parabegin,
                paraend,
                CFR_Text,
                ParagraphList,
                ParagraphList[counter]
            )

            # Fuegt interne Einzelverweise zur Verweisliste des aktuellen Artikels hinzu.
            Verweise += verweise

            # Fuegt externe Einzelverweise zur externen Verweisliste hinzu.
            ExterneVerweise += externe_verweise

            # Fuegt CRR-Einzelverweise zur CRR-Verweisliste hinzu.
            CRRVerweise += crr_verweise

        # Entfernt doppelte interne Verweise, behaelt aber die erste Fundreihenfolge bei.
        Verweise_clean = []
        for v in Verweise:
            if v not in Verweise_clean:
                Verweise_clean.append(v)

        # Speichert die internen Verweise fuer den aktuellen Artikel.
        ParagraphVerweise.append(Verweise_clean)

        # Entfernt doppelte externe Verweise, behaelt aber die erste Fundreihenfolge bei.
        ExterneVerweise_clean = []
        for v in ExterneVerweise:
            if v not in ExterneVerweise_clean:
                ExterneVerweise_clean.append(v)

        # Speichert die externen Verweise fuer den aktuellen Artikel separat.
        ParagraphExternalVerweise.append(ExterneVerweise_clean)

        # Entfernt doppelte CRR-Verweise, behaelt aber die erste Fundreihenfolge bei.
        CRRVerweise_clean = []
        for v in CRRVerweise:
            if v not in CRRVerweise_clean:
                CRRVerweise_clean.append(v)

        # Speichert die CRR-Verweise fuer den aktuellen Artikel separat.
        ParagraphCRRVerweise.append(CRRVerweise_clean) 
    
   
    # Kontrollausgaben fuer den aktuellen Anpassungsschritt.
    print("Anzahl Artikel:", len(ParagraphList))
    print("Anzahl interne Verweislisten:", len(ParagraphVerweise))
    print("Anzahl externe Verweislisten:", len(ParagraphExternalVerweise))
    print("Anzahl CRR-Verweislisten:", len(ParagraphCRRVerweise))
    print("Interne Einzelverweise insgesamt:", sum([len(x) for x in ParagraphVerweise]))
    print("Externe Einzelverweise insgesamt:", sum([len(x) for x in ParagraphExternalVerweise]))
    print("CRR-Einzelverweise insgesamt:", sum([len(x) for x in ParagraphCRRVerweise]))
    print("Artikel mit internen Einzelverweisen:", sum([len(x) > 0 for x in ParagraphVerweise]))
    print("Artikel mit externen Einzelverweisen:", sum([len(x) > 0 for x in ParagraphExternalVerweise]))
    print("Artikel mit CRR-Einzelverweisen:", sum([len(x) > 0 for x in ParagraphCRRVerweise]))

    print("")
    print("Erste interne Treffer:")
    printed = 0
    for i in range(len(ParagraphList)):
        if len(ParagraphVerweise[i]) > 0:
            print("Artikel", ParagraphList[i], "->", ParagraphVerweise[i])
            printed += 1
        if printed == 15:
            break

    print("")
    print("Erste externe Treffer:")
    printed = 0
    for i in range(len(ParagraphList)):
        if len(ParagraphExternalVerweise[i]) > 0:
            print("Artikel", ParagraphList[i], "->", ParagraphExternalVerweise[i])
            printed += 1
        if printed == 15:
            break

    print("")
    print("Erste CRR-Treffer:")
    printed = 0
    for i in range(len(ParagraphList)):
        if len(ParagraphCRRVerweise[i]) > 0:
            print("Artikel", ParagraphList[i], "->", ParagraphCRRVerweise[i])
            printed += 1
        if printed == 15: 
            break 


    # 4)Mehrfachverweise 
    
    



