
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
    crd_file_name = "C:/Users/jalal/OneDrive/Desktop/MASTERARBEIT/Texte/txt/CELEX_32013L0036_EN_TXT.txt"
    crr_file_name = f"C:/Users/jalal/OneDrive/Desktop/MASTERARBEIT/Texte/CRR_Texte/CRR_{year}.txt"

    print("CRD-Datei:", crd_file_name)
    print("CRR-Datei:", crr_file_name)

    CRD_Text = load_text(crd_file_name)
    CRR_Text = load_text(crr_file_name)

    print("CRD-Textlaenge:", len(CRD_Text))
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


    PositionsParagraph = []
    EndParagraph = []
    ParagraphList = []
    import re
    # CRD: Artikelüberschriften erkennen, z.B.:
    # "\nArticle 1\n"
    # "\n Article 1\n"
    # "\n   Article 1\n"
    pattern = r"\n[ ]{0,3}Article\s+(\d+)\n" #\n bedeutet Zeilenumbruch, [ ]{0,3} bedeutet 0 bis 3 Leerzeichen,
                                             #Article\s+(\d+) bedeutet das Wort Article gefolgt von einem oder mehreren Leerzeichen und dann einer oder mehreren Ziffern
                                             #die in Klammern gespeichert werden (\d+),
                                             #\n am Ende bedeutet dass der Artikelname mit einem Zeilenumbruch endet.

    matches = list(re.finditer(pattern, CFR_Text)) # die Lsit-funktion erstellt eine Liste aller gefunden treffer im gesamten Text.
                                                    # somt sind matches eine Lister aller gefunden treffer 

    #print("Gefundene Artikel (roh):", len(matches))

    for i in range(len(matches)):

        # Nummer des aktuellen Artikels, analog zur ParagraphList im Originalcode.
        ParagraphList.append(matches[i].group(1))

        # Beginn des aktuellen Artikels
        parabegin = matches[i].start()

        # Ende des aktuellen Artikels
        if i < len(matches) - 1:
            paraend = matches[i + 1].start()
        else:
            # Begrenzung des letzten Artikels:
            # Nach Article 165 folgen noch Annex und Schlussformeln.
            possible_ends = []

            for marker in ["\nANNEX I", "\nANNEX", "\nDone at Brussels"]:
                pos = CFR_Text.find(marker, parabegin)
                if pos != -1 and pos > parabegin:
                    possible_ends.append(pos)

            if len(possible_ends) > 0:
                paraend = min(possible_ends)
            else:
                paraend = len(CFR_Text)

        PositionsParagraph.append(parabegin)
        EndParagraph.append(paraend)

    #print("Anzahl Artikel:", len(ParagraphList))
    #print("Erster Artikel:", ParagraphList[0])
    #print("Letzter Artikel:", ParagraphList[-1])
 
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
    
    



