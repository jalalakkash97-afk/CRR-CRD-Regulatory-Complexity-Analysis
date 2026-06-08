
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

    CFR_Text = CRD_Text

    ##################################################################
    ################# 2) Paragraphenfänge bestimmen ##################
    ##################################################################

    import re

    def erkenne_artikel_im_eu_text(text):
        positions = []
        ends = []
        artikel_liste = []

        pattern = r"\n[ ]{0,3}Article\s+(\d+)\n"
        matches = list(re.finditer(pattern, text))

        for i in range(len(matches)):
            artikel_liste.append(matches[i].group(1))
            artikelfang = matches[i].start()

            if i < len(matches) - 1:
                artikelende = matches[i + 1].start()
            else:
                possible_ends = []
                for marker in ["\nANNEX I", "\nANNEX", "\nDone at Brussels"]:
                    pos = text.find(marker, artikelfang)
                    if pos != -1 and pos > artikelfang:
                        possible_ends.append(pos)

                if len(possible_ends) > 0:
                    artikelende = min(possible_ends)
                else:
                    artikelende = len(text)

            positions.append(artikelfang)
            ends.append(artikelende)

        return positions, ends, artikel_liste

    PositionsParagraph_CRD, EndParagraph_CRD, ParagraphList_CRD = erkenne_artikel_im_eu_text(CRD_Text)
    PositionsParagraph_CRR, EndParagraph_CRR, ParagraphList_CRR = erkenne_artikel_im_eu_text(CRR_Text)

    print("CRD-Artikel:", len(ParagraphList_CRD))
    print("CRR-Artikel:", len(ParagraphList_CRR))

    CRD_artikel=[]    
    CRR_artikel=[]
    for i in range(len(ParagraphList_CRD)):
        CRD_artikel.append("CRD_" + ParagraphList_CRD[i])
    for i in range(len(ParagraphList_CRR)):
        CRR_artikel.append("CRR_" + ParagraphList_CRR[i]) 
    
    for i in range(min(10, len(CRD_artikel))):
        print(CRD_artikel[i])   
    

    ParagraphList_All = CRD_artikel + CRR_artikel

    print("Artikel gesamt (CRD + CRR):", len(ParagraphList_All))

    PositionsParagraph = PositionsParagraph_CRD
    EndParagraph = EndParagraph_CRD
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
    
    



