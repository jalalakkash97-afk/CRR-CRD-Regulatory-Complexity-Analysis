
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

    ##################################################################
    ################# 3) Verweise in jedem Paragraph identifizieren ##
    ##################################################################

    # Gemeinsame Ergebnisliste fuer die spaetere Berechnung.
    # Die Reihenfolge soll spaeter zu ParagraphList_All passen:
    # zuerst alle CRD-Artikel, danach alle CRR-Artikel.
    ParagraphVerweise = []

    # Getrennte Statistiklisten fuer den CRD.
    ParagraphVerweise_CRD_gleicher_Rechtsakt = []
    ParagraphVerweise_CRD_anderer_Rechtsakt = []
    ParagraphVerweise_CRD_extern = []
    ParagraphVerweise_CRD_gesamt = []

    # Getrennte Statistiklisten fuer den CRR.
    ParagraphVerweise_CRR_gleicher_Rechtsakt = []
    ParagraphVerweise_CRR_anderer_Rechtsakt = []
    ParagraphVerweise_CRR_extern = []
    ParagraphVerweise_CRR_gesamt = []

    # Hilfsfunktion: entfernt doppelte Eintraege, behaelt aber die erste Fundreihenfolge bei.
    def unique_list(values):
        values_clean = []
        for value in values:
            if value not in values_clean:
                values_clean.append(value)
        return values_clean

    # Hilfsfunktion: fuehrt die Einzelverweiserkennung fuer einen Rechtsakt durch.
    # Dadurch bleibt der Hauptblock unten kuerzer und CRD/CRR werden einheitlich behandelt.
    def sammle_einzelverweise_fuer_rechtsakt(
        text,
        positions_paragraph,
        end_paragraph,
        paragraph_list,
        current_act,
    ):
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

            verweise_berechnung_alle.append(unique_list(Verweise_Berechnung))
            verweise_gleicher_rechtsakt_alle.append(unique_list(Verweise_gleicher_Rechtsakt))
            verweise_anderer_rechtsakt_alle.append(unique_list(Verweise_anderer_Rechtsakt))
            verweise_extern_alle.append(unique_list(Verweise_extern))
            verweise_gesamt_alle.append(unique_list(Verweise_gesamt))

        return (
            verweise_berechnung_alle,
            verweise_gleicher_rechtsakt_alle,
            verweise_anderer_rechtsakt_alle,
            verweise_extern_alle,
            verweise_gesamt_alle,
        )

    # Diese Zaehler bleiben aus der Originalstruktur erhalten.
    # Fuer einfache Einzelverweise werden sie noch nicht gebraucht.
    counter_non_identified_ref = 0
    counter_multi_ref = 0
    counter_non_identified_ref2 = 0

    # ---------- CRD: Einzelverweise erkennen ----------
    (
        ParagraphVerweise_CRD_berechnung,
        ParagraphVerweise_CRD_gleicher_Rechtsakt,
        ParagraphVerweise_CRD_anderer_Rechtsakt,
        ParagraphVerweise_CRD_extern,
        ParagraphVerweise_CRD_gesamt,
    ) = sammle_einzelverweise_fuer_rechtsakt(
        CRD_Text,
        PositionsParagraph_CRD,
        EndParagraph_CRD,
        ParagraphList_CRD,
        "CRD",
    )

    # ---------- CRR: Einzelverweise erkennen ----------
    (
        ParagraphVerweise_CRR_berechnung,
        ParagraphVerweise_CRR_gleicher_Rechtsakt,
        ParagraphVerweise_CRR_anderer_Rechtsakt,
        ParagraphVerweise_CRR_extern,
        ParagraphVerweise_CRR_gesamt,
    ) = sammle_einzelverweise_fuer_rechtsakt(
        CRR_Text,
        PositionsParagraph_CRR,
        EndParagraph_CRR,
        ParagraphList_CRR,
        "CRR",
    )

    # Gemeinsame Verweisliste fuer die spaetere Berechnung.
    # Die Reihenfolge muss zu ParagraphList_All passen:
    # zuerst CRD, danach CRR.
    ParagraphVerweise = ParagraphVerweise_CRD_berechnung + ParagraphVerweise_CRR_berechnung

    # Gemeinsame Knotenliste fuer den Einzelverweis-Stand.
    ParagraphList = ParagraphList_All

    # Kontrollausgaben fuer den aktuellen Einzelverweis-Stand.
    print("")
    print("Einzelverweise CRD")
    print("CRD -> CRD:", sum([len(x) for x in ParagraphVerweise_CRD_gleicher_Rechtsakt]))
    print("CRD -> CRR:", sum([len(x) for x in ParagraphVerweise_CRD_anderer_Rechtsakt]))
    print("CRD -> extern:", sum([len(x) for x in ParagraphVerweise_CRD_extern]))
    print("CRD gesamt:", sum([len(x) for x in ParagraphVerweise_CRD_gesamt]))

    print("")
    print("Einzelverweise CRR")
    print("CRR -> CRR:", sum([len(x) for x in ParagraphVerweise_CRR_gleicher_Rechtsakt]))
    print("CRR -> CRD:", sum([len(x) for x in ParagraphVerweise_CRR_anderer_Rechtsakt]))
    print("CRR -> extern:", sum([len(x) for x in ParagraphVerweise_CRR_extern]))
    print("CRR gesamt:", sum([len(x) for x in ParagraphVerweise_CRR_gesamt]))

    print("")
    print("Berechnungslisten gesamt:", len(ParagraphVerweise))
    print("Interne Verweise fuer Berechnung gesamt:", sum([len(x) for x in ParagraphVerweise]))

    print("")
    print("Erste CRD-Treffer fuer Berechnung:")
    printed = 0
    for i in range(len(CRD_artikel)):
        if len(ParagraphVerweise[i]) > 0:
            print(CRD_artikel[i], "->", ParagraphVerweise[i])
            printed += 1
        if printed == 15:
            break

    print("")
    print("Erste CRR-Treffer fuer Berechnung:")
    printed = 0
    for i in range(len(CRR_artikel)):
        index_gesamt = len(CRD_artikel) + i
        if len(ParagraphVerweise[index_gesamt]) > 0:
            print(CRR_artikel[i], "->", ParagraphVerweise[index_gesamt])
            printed += 1
        if printed == 15:
            break


    # 4)Mehrfachverweise 
    
    



