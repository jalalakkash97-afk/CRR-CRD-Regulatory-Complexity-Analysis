
import numpy as np
from functools import cmp_to_key
import copy

from einzelverweise import einzelverweise
from einzelverweise_crd import einzelverweise_crd
from einzelverweise_crr import einzelverweise_crr
from paragraph_begin_end import paragraphenbeginend
from mehrfachverweise import mehrfachverweise
from mehrfachverweise_crd import mehrfachverweise_crd
from mehrfachverweise_crr import mehrfachverweise_crr
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
from compute_statistics_crd_crr import compute_statistics_crd_crr
from write_output import write_output
from write_output_crd_crr import write_output_crd_crr



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
        # - eine oder mehrere Ziffern und optional einen Buchstaben als Artikelnummer,
        # - und danach wieder einen Zeilenumbruch.
        # Dadurch bleiben Article 10 und Article 10a zwei getrennte Artikel.
        # Klammerangaben wie Article 10(1)(a) sind keine Ueberschriften und werden hier nicht erfasst.
        pattern = r"\n[ ]{0,3}Article[ \t\u00a0]+(\d+[a-zA-Z]*)[ \t\u00a0]*\n"

        # Anhaenge koennen Tabellen mit erneut ausgeschriebenen Artikelnummern enthalten.
        # Fuer die Artikelerkennung wird der Text deshalb am ersten echten Anhang nach
        # dem Beginn des Rechtstextes abgeschnitten.
        erster_artikel = re.search(pattern, text)
        analyseende = len(text)
        if erster_artikel is not None:
            anhang = re.search(
                r"\n[ ]{0,3}ANNEX(?:\s+I)?\s*\n",
                text[erster_artikel.start():],
            )
            if anhang is not None:
                analyseende = erster_artikel.start() + anhang.start()

        # Sucht alle passenden Artikelueberschriften nur im eigentlichen Rechtstext.
        matches = list(re.finditer(pattern, text[:analyseende]))

        # Geht alle gefundenen Artikelueberschriften nacheinander durch.
        for i in range(len(matches)):
            # Speichert die Artikelnummer des aktuellen Treffers.
            artikel_liste.append(matches[i].group(1).lower())    # Gruppe 1 ist die vollstaendige Artikelnummer.
            # Speichert die Startposition des aktuellen Artikels.
            artikelfang = matches[i].start()

            # Wenn noch ein weiterer Artikel folgt, endet der aktuelle Artikel direkt vor dem naechsten.
            if i < len(matches) - 1:
                artikelende = matches[i + 1].start()
            else:
                # Letzten Artikel vor Anhaengen oder Schlussformeln begrenzen.
                # Diese Marker liegen typischerweise nach dem eigentlichen Rechtstext.
                possible_ends = []
                # Prueft mehrere moegliche Endmarker, damit die Logik sowohl bei CRD als auch bei CRR robust bleibt.
                for marker in ["\nDone at Brussels"]:
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
                    artikelende = analyseende

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

    # Ergebnislisten fuer alle Artikelverweise aus der CRD.
    # Enthalten sind Einzelverweise und Mehrfachverweise zusammen.
    # Jede Position entspricht einem Artikel aus ParagraphList_CRD.
    Artikelverweise_CRD_zu_CRD = []
    Artikelverweise_CRD_zu_extern = []
    Artikelverweise_CRD_zu_CRR = []

    # Ergebnislisten fuer alle Artikelverweise aus der CRR.
    # Enthalten sind Einzelverweise und Mehrfachverweise zusammen.
    # Jede Position entspricht einem Artikel aus ParagraphList_CRR.
    Artikelverweise_CRR_zu_CRR = []
    Artikelverweise_CRR_zu_extern = []
    Artikelverweise_CRR_zu_CRD = []

    # Diese Zaehler bleiben aus der Originalstruktur erhalten.
    # Fuer einfache Einzelverweise werden sie noch nicht gebraucht.
    counter_non_identified_ref = 0
    counter_multi_ref = 0
    counter_non_identified_ref2 = 0

    # Schreibweisen fuer einfache Einzelverweise.
    # In diesem ersten Schritt suchen wir nur nach Singularformen wie "Article 30".
    ParagraphSignArray = ["Article"]

    # Geht durch alle gefundenen CRD-Artikel.
    for counter in range(len(PositionsParagraph_CRD)):

        # Beginn des aktuellen CRD-Artikels.
        parabegin = PositionsParagraph_CRD[counter]

        # Ende des aktuellen CRD-Artikels.
        paraend = EndParagraph_CRD[counter]

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
                CRD_Text,
                ParagraphList_CRD,
                ParagraphList_CRD[counter]
            )

            # Fuegt interne Einzelverweise zur Verweisliste des aktuellen Artikels hinzu.
            Verweise += verweise

            # Fuegt externe Einzelverweise zur externen Verweisliste hinzu.
            ExterneVerweise += externe_verweise

            # Fuegt CRR-Einzelverweise zur CRR-Verweisliste hinzu.
            CRRVerweise += crr_verweise

        # Sucht Mehrfachverweise wie "Articles 10 to 14" im aktuellen CRD-Artikel.
        verweise, externe_verweise, crr_verweise, counter_multi_ref, counter_non_identified_ref, counter_non_identified_ref2 = mehrfachverweise_crd(
            parabegin,
            paraend,
            counter_multi_ref,
            counter_non_identified_ref,
            counter_non_identified_ref2,
            CRD_Text,
            ParagraphList_CRD,
            ParagraphList_CRD[counter]
        )

        # Fuegt interne CRD-Mehrfachverweise zur Verweisliste hinzu.
        Verweise += verweise

        # Fuegt externe Mehrfachverweise zur externen Verweisliste hinzu.
        ExterneVerweise += externe_verweise

        # Fuegt CRR-Mehrfachverweise zur CRR-Verweisliste hinzu.
        CRRVerweise += crr_verweise

        # Entfernt doppelte interne Verweise, behaelt aber die erste Fundreihenfolge bei.
        Verweise_clean = []
        for v in Verweise:
            if v not in Verweise_clean:
                Verweise_clean.append(v)

        # Speichert die internen CRD-Verweise fuer den aktuellen CRD-Artikel.
        Artikelverweise_CRD_zu_CRD.append(Verweise_clean)

        # Entfernt doppelte externe Verweise, behaelt aber die erste Fundreihenfolge bei.
        ExterneVerweise_clean = []
        for v in ExterneVerweise:
            if v not in ExterneVerweise_clean:
                ExterneVerweise_clean.append(v)

        # Speichert die externen Verweise fuer den aktuellen CRD-Artikel separat.
        Artikelverweise_CRD_zu_extern.append(ExterneVerweise_clean)

        # Entfernt doppelte CRR-Verweise, behaelt aber die erste Fundreihenfolge bei.
        CRRVerweise_clean = []
        for v in CRRVerweise:
            if v not in CRRVerweise_clean:
                CRRVerweise_clean.append(v)

        # Speichert die CRR-Verweise fuer den aktuellen CRD-Artikel separat.
        Artikelverweise_CRD_zu_CRR.append(CRRVerweise_clean)

    # Geht durch alle gefundenen CRR-Artikel.
    for counter in range(len(PositionsParagraph_CRR)):

        # Beginn des aktuellen CRR-Artikels.
        parabegin = PositionsParagraph_CRR[counter]

        # Ende des aktuellen CRR-Artikels.
        paraend = EndParagraph_CRR[counter]

        # Interne Verweise des aktuellen CRR-Artikels.
        Verweise = []

        # Externe Verweise des aktuellen CRR-Artikels.
        ExterneVerweise = []

        # CRD-Verweise des aktuellen CRR-Artikels.
        CRDVerweise = []

        # Geht durch alle Suchsignale fuer einfache Artikelverweise.
        for index_i in range(len(ParagraphSignArray)):

            # Aktuelles Suchsignal, hier erstmal nur "Article".
            ParagraphSign = ParagraphSignArray[index_i]

            # Sucht einfache Artikelverweise im aktuellen CRR-Artikel.
            verweise, externe_verweise, crd_verweise = einzelverweise_crr(
                ParagraphSign,
                parabegin,
                paraend,
                CRR_Text,
                ParagraphList_CRR,
                ParagraphList_CRR[counter]
            )

            # Fuegt interne CRR-Einzelverweise zur Verweisliste hinzu.
            Verweise += verweise

            # Fuegt externe Einzelverweise zur externen Verweisliste hinzu.
            ExterneVerweise += externe_verweise

            # Fuegt CRD-Einzelverweise zur CRD-Verweisliste hinzu.
            CRDVerweise += crd_verweise

        # Sucht Mehrfachverweise wie "Articles 32 to 35" im aktuellen CRR-Artikel.
        verweise, externe_verweise, crd_verweise, counter_multi_ref, counter_non_identified_ref, counter_non_identified_ref2 = mehrfachverweise_crr(
            parabegin,
            paraend,
            counter_multi_ref,
            counter_non_identified_ref,
            counter_non_identified_ref2,
            CRR_Text,
            ParagraphList_CRR,
            ParagraphList_CRR[counter]
        )

        # Fuegt interne CRR-Mehrfachverweise zur Verweisliste hinzu.
        Verweise += verweise

        # Fuegt externe Mehrfachverweise zur externen Verweisliste hinzu.
        ExterneVerweise += externe_verweise

        # Fuegt CRD-Mehrfachverweise zur CRD-Verweisliste hinzu.
        CRDVerweise += crd_verweise

        # Entfernt doppelte interne CRR-Verweise, behaelt aber die erste Fundreihenfolge bei.
        Verweise_clean = []
        for v in Verweise:
            if v not in Verweise_clean:
                Verweise_clean.append(v)

        # Speichert die internen CRR-Verweise fuer den aktuellen CRR-Artikel.
        Artikelverweise_CRR_zu_CRR.append(Verweise_clean)

        # Entfernt doppelte externe Verweise, behaelt aber die erste Fundreihenfolge bei.
        ExterneVerweise_clean = []
        for v in ExterneVerweise:
            if v not in ExterneVerweise_clean:
                ExterneVerweise_clean.append(v)

        # Speichert die externen Verweise fuer den aktuellen CRR-Artikel separat.
        Artikelverweise_CRR_zu_extern.append(ExterneVerweise_clean)

        # Entfernt doppelte CRD-Verweise, behaelt aber die erste Fundreihenfolge bei.
        CRDVerweise_clean = []
        for v in CRDVerweise:
            if v not in CRDVerweise_clean:
                CRDVerweise_clean.append(v)

        # Speichert die CRD-Verweise fuer den aktuellen CRR-Artikel separat.
        Artikelverweise_CRR_zu_CRD.append(CRDVerweise_clean)

    ##################################################################
    ################# 3b) Gemeinsame Rechenstruktur fuer die Berechnung bauen ############
    ##################################################################

    # Ab hier wird aus den getrennten CRD-/CRR-Verweislisten eine gemeinsame Rechenliste gebaut.
    # Externe Verweise bleiben draussen, weil sie nur fuer die Statistik verwendet werden.

    # Diese Hilfsfunktion entfernt Dopplungen und behaelt die erste Fundreihenfolge bei.
    def eindeutige_liste(werte):
        # Ergebnisliste fuer die bereinigten Werte.
        ergebnis = []

        # Geht jeden gefundenen Verweis der Reihe nach durch.
        for wert in werte:
            # Uebernimmt den Verweis nur, wenn er noch nicht in der Ergebnisliste steht.
            if wert not in ergebnis:
                # Fuegt den bisher noch nicht enthaltenen Verweis hinzu.
                ergebnis.append(wert)

        # Gibt die bereinigte Liste zurueck.
        return ergebnis

    # In dieser Liste stehen die berechnungsrelevanten Verweise der CRD-Artikel.
    ParagraphVerweise_CRD_Berechnung = []

    # Geht alle CRD-Artikel durch.
    for counter in range(len(ParagraphList_CRD)):
        # CRD-interne Verweise bekommen den Praefix "CRD_".
        verweise_auf_crd = ["CRD_" + verweis for verweis in Artikelverweise_CRD_zu_CRD[counter]]

        # Verweise von der CRD auf die CRR bekommen den Praefix "CRR_".
        verweise_auf_crr = ["CRR_" + verweis for verweis in Artikelverweise_CRD_zu_CRR[counter]]

        # Fuer die Berechnung gelten CRD->CRD und CRD->CRR gemeinsam als interne Verweise.
        verweise_gesamt = verweise_auf_crd + verweise_auf_crr

        # Speichert die bereinigte Verweisliste des aktuellen CRD-Artikels.
        ParagraphVerweise_CRD_Berechnung.append(eindeutige_liste(verweise_gesamt))

    # In dieser Liste stehen die berechnungsrelevanten Verweise der CRR-Artikel.
    ParagraphVerweise_CRR_Berechnung = []

    # Geht alle CRR-Artikel durch.
    for counter in range(len(ParagraphList_CRR)):
        # CRR-interne Verweise bekommen den Praefix "CRR_".
        verweise_auf_crr = ["CRR_" + verweis for verweis in Artikelverweise_CRR_zu_CRR[counter]]

        # Verweise von der CRR auf die CRD bekommen den Praefix "CRD_".
        verweise_auf_crd = ["CRD_" + verweis for verweis in Artikelverweise_CRR_zu_CRD[counter]]

        # Fuer die Berechnung gelten CRR->CRR und CRR->CRD gemeinsam als interne Verweise.
        verweise_gesamt = verweise_auf_crr + verweise_auf_crd

        # Speichert die bereinigte Verweisliste des aktuellen CRR-Artikels.
        ParagraphVerweise_CRR_Berechnung.append(eindeutige_liste(verweise_gesamt))

    # Diese Liste hat dieselbe Reihenfolge wie ParagraphList_All:
    # erst alle CRD-Artikel, danach alle CRR-Artikel.
    ParagraphVerweise_All = ParagraphVerweise_CRD_Berechnung + ParagraphVerweise_CRR_Berechnung

    # Prueft, ob jede Verweisliste genau einem Artikel aus ParagraphList_All entspricht.
    if len(ParagraphVerweise_All) != len(ParagraphList_All):
        # Kontrollmeldung fuer den Fall, dass beim Zusammenfuehren etwas nicht passt.
        print("WARNUNG: ParagraphList_All und ParagraphVerweise_All haben unterschiedliche Laengen.")

    # Sammelt alle Verweise, deren Ziel nicht in der gemeinsamen Artikelliste enthalten ist.
    FehlendeInterneVerweise = []

    # Geht jeden Artikel der gemeinsamen Liste durch.
    for counter in range(len(ParagraphVerweise_All)):
        # Geht alle berechnungsrelevanten Verweise des aktuellen Artikels durch.
        for verweis in ParagraphVerweise_All[counter]:
            # Ein interner Verweis muss in ParagraphList_All existieren.
            if verweis not in ParagraphList_All:
                # Speichert Quelle und Ziel, damit ein Fehler leicht kontrolliert werden kann.
                FehlendeInterneVerweise.append((ParagraphList_All[counter], verweis))
    
   
    # Kontrollausgaben fuer den aktuellen Anpassungsschritt.
    print("")
    print("Artikelverweise CRD")
    print("Anzahl CRD-Artikel:", len(ParagraphList_CRD))
    print("CRD -> CRD:", sum([len(x) for x in Artikelverweise_CRD_zu_CRD]))
    print("CRD -> CRR:", sum([len(x) for x in Artikelverweise_CRD_zu_CRR]))
    print("CRD -> externe Rechtsakte:", sum([len(x) for x in Artikelverweise_CRD_zu_extern]))
    print("CRD gesamt:", sum([len(x) for x in Artikelverweise_CRD_zu_CRD]) + sum([len(x) for x in Artikelverweise_CRD_zu_CRR]) + sum([len(x) for x in Artikelverweise_CRD_zu_extern]))

    print("")
    print("Artikelverweise CRR")
    print("Anzahl CRR-Artikel:", len(ParagraphList_CRR))
    print("CRR -> CRR:", sum([len(x) for x in Artikelverweise_CRR_zu_CRR]))
    print("CRR -> CRD:", sum([len(x) for x in Artikelverweise_CRR_zu_CRD]))
    print("CRR -> externe Rechtsakte:", sum([len(x) for x in Artikelverweise_CRR_zu_extern]))
    print("CRR gesamt:", sum([len(x) for x in Artikelverweise_CRR_zu_CRR]) + sum([len(x) for x in Artikelverweise_CRR_zu_CRD]) + sum([len(x) for x in Artikelverweise_CRR_zu_extern]))

    print("")
    print("Gemeinsame Rechenstruktur")
    print("Artikel gesamt:", len(ParagraphList_All))
    print("Verweislisten gesamt:", len(ParagraphVerweise_All))
    print("Interne Verweise fuer Berechnung:", sum([len(x) for x in ParagraphVerweise_All]))
    print("Fehlende interne Zielartikel:", len(FehlendeInterneVerweise))

    print("")
    print("Erste CRD-internen Treffer:")
    printed = 0
    for i in range(len(ParagraphList_CRD)):
        if len(Artikelverweise_CRD_zu_CRD[i]) > 0:
            print("CRD_" + ParagraphList_CRD[i], "->", ["CRD_" + v for v in Artikelverweise_CRD_zu_CRD[i]])
            printed += 1
        if printed == 15:
            break

    print("")
    print("Erste CRD-externen Treffer:")
    printed = 0
    for i in range(len(ParagraphList_CRD)):
        if len(Artikelverweise_CRD_zu_extern[i]) > 0:
            print("CRD_" + ParagraphList_CRD[i], "->", Artikelverweise_CRD_zu_extern[i])
            printed += 1
        if printed == 15:
            break

    print("")
    print("Erste CRD-auf-CRR-Treffer:")
    printed = 0
    for i in range(len(ParagraphList_CRD)):
        if len(Artikelverweise_CRD_zu_CRR[i]) > 0:
            print("CRD_" + ParagraphList_CRD[i], "->", ["CRR_" + v for v in Artikelverweise_CRD_zu_CRR[i]])
            printed += 1
        if printed == 15: 
            break 

    print("")
    print("Erste CRR-internen Treffer:")
    printed = 0
    for i in range(len(ParagraphList_CRR)):
        if len(Artikelverweise_CRR_zu_CRR[i]) > 0:
            print("CRR_" + ParagraphList_CRR[i], "->", ["CRR_" + v for v in Artikelverweise_CRR_zu_CRR[i]])
            printed += 1
        if printed == 15:
            break

    print("")
    print("Erste CRR-auf-CRD-Treffer:")
    printed = 0
    for i in range(len(ParagraphList_CRR)):
        if len(Artikelverweise_CRR_zu_CRD[i]) > 0:
            print("CRR_" + ParagraphList_CRR[i], "->", ["CRD_" + v for v in Artikelverweise_CRR_zu_CRD[i]])
            printed += 1
        if printed == 15:
            break

    ##################################################################
    ################# 4) Operatoren und Lesbarkeit berechnen #########
    ##################################################################

    # Das gemeinsame Operatorenwoerterbuch bleibt wie im Originalcode aufgebaut.
    dictionary_ = reg_operators + log_operators + math_operators

    # Zaehlt alle Operatoren je CRD-Artikel.
    Operators_per_Paragraph_CRD = operator_counting(
        dictionary_,
        ParagraphList_CRD,
        PositionsParagraph_CRD,
        EndParagraph_CRD,
        CRD_Text
    )

    # Zaehlt alle Operatoren je CRR-Artikel.
    Operators_per_Paragraph_CRR = operator_counting(
        dictionary_,
        ParagraphList_CRR,
        PositionsParagraph_CRR,
        EndParagraph_CRR,
        CRR_Text
    )

    # Zaehlt nur regulatorische Operatoren je CRD-Artikel.
    Reg_Operators_per_Paragraph_CRD = operator_counting(
        reg_operators,
        ParagraphList_CRD,
        PositionsParagraph_CRD,
        EndParagraph_CRD,
        CRD_Text
    )

    # Zaehlt nur regulatorische Operatoren je CRR-Artikel.
    Reg_Operators_per_Paragraph_CRR = operator_counting(
        reg_operators,
        ParagraphList_CRR,
        PositionsParagraph_CRR,
        EndParagraph_CRR,
        CRR_Text
    )

    # Fuehrt die Operatorenlisten in derselben Reihenfolge wie ParagraphList_All zusammen:
    # zuerst CRD, danach CRR.
    Operators_per_Paragraph = Operators_per_Paragraph_CRD + Operators_per_Paragraph_CRR
    Reg_Operators_per_Paragraph = Reg_Operators_per_Paragraph_CRD + Reg_Operators_per_Paragraph_CRR

    # Sichert die ungegewichteten regulatorischen Operatoren.
    # Diese Liste kann spaeter fuer Kontrollrechnungen oder Ausgaben verwendet werden.
    Reg_Operators_alone = copy.deepcopy(Reg_Operators_per_Paragraph)

    # Berechnet die Flesch-Reading-Ease-Komponenten fuer die CRD.
    (FRESPara_CRD, NumParaSent_CRD, NumParaWords_CRD, NumParaSylla_CRD) = computing_fres(
        ParagraphList_CRD,
        PositionsParagraph_CRD,
        EndParagraph_CRD,
        CRD_Text
    )

    # Berechnet die Flesch-Reading-Ease-Komponenten fuer die CRR.
    (FRESPara_CRR, NumParaSent_CRR, NumParaWords_CRR, NumParaSylla_CRR) = computing_fres(
        ParagraphList_CRR,
        PositionsParagraph_CRR,
        EndParagraph_CRR,
        CRR_Text
    )

    # Fuehrt die Lesbarkeitswerte ebenfalls in der Reihenfolge von ParagraphList_All zusammen.
    FRESPara = FRESPara_CRD + FRESPara_CRR
    NumParaSent = NumParaSent_CRD + NumParaSent_CRR
    NumParaWords = NumParaWords_CRD + NumParaWords_CRR
    NumParaSylla = NumParaSylla_CRD + NumParaSylla_CRR

    # Gewichtet die regulatorischen Operatoren mit dem FRES-Wert wie im Originalcode.
    for index_p in range(len(ParagraphList_All)):
        Reg_Operators_per_Paragraph[index_p] = round(
            Reg_Operators_per_Paragraph[index_p] * (1 - (FRESPara[index_p] - 60) / 60)
        )

    # Ab hier werden die gemeinsamen Listen auf die Originalnamen gelegt.
    # Dadurch kann der folgende Berechnungsteil moeglichst nah am Originalcode bleiben.
    ParagraphList = ParagraphList_All
    ParagraphVerweise = ParagraphVerweise_All

    # Grundgroessen fuer die spaetere Komplexitaetsberechnung.
    sum_reg_oper = sum(Reg_Operators_per_Paragraph)
    num_para = len(ParagraphList)

    print("")
    print("Operatoren und Lesbarkeit")
    print("Operatorenlisten gesamt:", len(Operators_per_Paragraph))
    print("Regulatorische Operatorenlisten gesamt:", len(Reg_Operators_per_Paragraph))
    print("FRES-Listen gesamt:", len(FRESPara))
    print("Summe gewichtete regulatorische Operatoren:", sum_reg_oper)

    ##################################################################
    ################# 5) Komplexitaet mit Verweisen berechnen ########
    ##################################################################

    # Parameter wie im Originalcode.
    exp_ref_factor = 1.1

    # Der Klumpenfaktor wird im Original gleich dem Verweisfaktor gesetzt.
    clumb_factor = exp_ref_factor

    # Nicht aufloesbare Verweise erhalten aktuell keine Zusatzkosten.
    # Externe Verweise sind hier ohnehin nicht in ParagraphVerweise enthalten.
    undef_ref_costs = 0

    # Fuehrt die eigentliche Komplexitaetsberechnung auf dem gemeinsamen CRD/CRR-Korpus aus.
    (
        Klumpenparagraph,
        ParagraphVerweiseKlumpen,
        ParagraphImplicitVerweiseKlumpen,
        ParagraphOperatorenKlumpen,
        ParagraphRegOperatorenKlumpen,
        reg_costs_vreg
    ) = compute_complexity(
        ParagraphList,
        ParagraphVerweise,
        Operators_per_Paragraph,
        Reg_Operators_per_Paragraph,
        Reg_Operators_alone,
        num_para,
        sum_reg_oper,
        undef_ref_costs,
        exp_ref_factor,
        clumb_factor
    )

    print("")
    print("Komplexitaetsberechnung")
    print("Berechnete Artikel:", len(reg_costs_vreg))
    print("Noch nicht berechnete Artikel:", sum([1 for x in reg_costs_vreg if x == -1]))
    print("Gesamtsumme Artikelkomplexitaeten:", sum(reg_costs_vreg))

    ##################################################################
    ################# 6) Kontrollauswertung der Komplexitaet #########
    ##################################################################

    # Bestimmt fuer jeden Klumpen den kleinsten enthaltenen Artikelindex.
    # Dadurch wird jeder Klumpen nur einmal gezaehlt.
    Repr_Klumpen = []

    # Geht alle Artikel durch.
    for index_p in range(len(Klumpenparagraph)):
        # Der kleinste Index dient als eindeutiger Vertreter des Klumpens.
        repr_index = min(Klumpenparagraph[index_p])

        # Fuegt den Vertreter nur einmal hinzu.
        if repr_index not in Repr_Klumpen:
            Repr_Klumpen.append(repr_index)

    # Sammelt alle Klumpen, die mehr als einen Artikel enthalten.
    Mehrartikel_Klumpen = []

    # Geht alle eindeutigen Klumpenvertreter durch.
    for repr_index in Repr_Klumpen:
        # Uebernimmt nur Klumpen mit mehr als einem Artikel.
        if len(Klumpenparagraph[repr_index]) > 1:
            Mehrartikel_Klumpen.append(Klumpenparagraph[repr_index])

    # Bestimmt den groessten Klumpen.
    if len(Mehrartikel_Klumpen) > 0:
        Groesster_Klumpen = max(Mehrartikel_Klumpen, key=len)
    else:
        Groesster_Klumpen = []

    # Baut eine Liste mit Artikelname, direktem Workload und finaler Komplexitaet.
    Artikel_Ergebnisse = []

    # Geht alle Artikel durch.
    for index_p in range(len(ParagraphList)):
        # Speichert die wichtigsten Werte je Artikel in einem Tupel.
        Artikel_Ergebnisse.append((
            ParagraphList[index_p],
            Reg_Operators_per_Paragraph[index_p],
            reg_costs_vreg[index_p],
            len(ParagraphVerweise[index_p])
        ))

    # Sortiert nach direktem Workload absteigend.
    Top_Direkter_Workload = sorted(Artikel_Ergebnisse, key=lambda x: x[1], reverse=True)[:10]

    # Sortiert nach finaler Komplexitaet inklusive Verweisen absteigend.
    Top_Komplexitaet_mit_Verweisen = sorted(Artikel_Ergebnisse, key=lambda x: x[2], reverse=True)[:10]

    print("")
    print("Kontrollauswertung Komplexitaet")
    print("Anzahl Klumpen gesamt:", len(Repr_Klumpen))
    print("Anzahl Klumpen mit mehr als einem Artikel:", len(Mehrartikel_Klumpen))
    print("Groesster Klumpen:", len(Groesster_Klumpen), "Artikel")

    if len(Groesster_Klumpen) > 0:
        print("Erste Artikel im groessten Klumpen:", [ParagraphList[i] for i in Groesster_Klumpen[:20]])

    print("")
    print("Top 10 direkter Workload")
    for artikel, direkter_workload, komplexitaet, anzahl_verweise in Top_Direkter_Workload:
        print(artikel, "->", direkter_workload, "| Verweise:", anzahl_verweise)

    print("")
    print("Top 10 Komplexitaet mit Verweisen")
    for artikel, direkter_workload, komplexitaet, anzahl_verweise in Top_Komplexitaet_mit_Verweisen:
        print(artikel, "->", komplexitaet, "| direkter Workload:", direkter_workload, "| Verweise:", anzahl_verweise)

    ##################################################################
    ################# 7) Berechnung der relevanten Statistiken ########
    ##################################################################

    (
        sum_reg_costs_vreg,
        num_great_lump,
        counter_cycl_compl,
        counter_quantity,
        counter_math,
        num_with_ref,
        fres_index,
        fres_total_syllables,
        fres_total_words,
        fres_total_sentence) = compute_statistics_crd_crr(
        ParagraphList,
        ParagraphVerweise,
        Klumpenparagraph,
        log_operators,
        reg_operators,
        math_operators,
        ParagraphList_CRD,
        PositionsParagraph_CRD,
        EndParagraph_CRD,
        CRD_Text,
        ParagraphList_CRR,
        PositionsParagraph_CRR,
        EndParagraph_CRR,
        CRR_Text,
        NumParaSent,
        NumParaWords,
        NumParaSylla,
        num_para,
        reg_costs_vreg
    )

    print("")
    print("Relevante Statistiken")
    print("Gesamtkomplexitaet mit Verweisen:", sum_reg_costs_vreg)
    print("Anzahl Mehrartikel-Klumpen:", num_great_lump)
    print("Logische Operatoren:", counter_cycl_compl)
    print("Regulatorische Operatoren:", counter_quantity)
    print("Mathematische Operatoren:", counter_math)
    print("Artikel mit internen Verweisen:", num_with_ref)
    print("FRES gesamt:", fres_index)

    ##################################################################
    ################# 8) Ausgabe der Ergebnisse ######################
    ##################################################################

    number_verweise = sum([len(x) for x in ParagraphVerweise])
    counter_missing = len(FehlendeInterneVerweise)

    write_output_crd_crr(
        year,
        exp_ref_factor,
        ParagraphList,
        ParagraphVerweise,
        number_verweise,
        counter_missing,
        Operators_per_Paragraph,
        Reg_Operators_per_Paragraph,
        Reg_Operators_alone,
        FRESPara,
        NumParaSent,
        NumParaWords,
        NumParaSylla,
        Klumpenparagraph,
        num_para,
        counter_cycl_compl,
        counter_quantity,
        counter_math,
        sum_reg_costs_vreg,
        num_with_ref,
        fres_index,
        fres_total_syllables,
        fres_total_words,
        fres_total_sentence,
        reg_costs_vreg
    )

    print("")
    print("Ergebnisse wurden geschrieben.")

