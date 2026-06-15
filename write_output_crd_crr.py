'''Funktion zur Ausgabe der Ergebnisse fuer CRD und CRR.'''

import csv


def excel_zahl(wert):
    """Formatiert Zahlen so, dass deutsches Excel Dezimalzahlen richtig liest."""

    if isinstance(wert, float):
        return str(wert).replace(".", ",")
    return wert


def write_output_crd_crr(
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
):
    ######################################################################
    ######### Ausgabe der zusammenfassenden Ergebnisdatei ################
    ######################################################################

    file_name = "ergebnisse_gesamt_crd_crr_" + str(year) + ".csv"

    with open(file_name, "w", newline="", encoding="utf-8-sig") as outfile:
        writer = csv.writer(outfile, delimiter=";")

        writer.writerow([
            "year",
            "exp_ref_factor",
            "number_articles",
            "number_references",
            "counter_missing",
            "sum_operators",
            "sum_reg_costs_vreg",
            "largest_clump",
            "counter_cycl_compl",
            "counter_quantity",
            "counter_math",
            "num_with_ref",
            "fres_index",
            "fres_total_syllables",
            "fres_total_words",
            "fres_total_sentence"
        ])

        writer.writerow([
            year,
            exp_ref_factor,
            len(ParagraphList),
            number_verweise,
            counter_missing,
            sum(Operators_per_Paragraph),
            excel_zahl(sum_reg_costs_vreg),
            max([len(Klumpenparagraph[i]) for i in range(num_para)]),
            counter_cycl_compl,
            counter_quantity,
            counter_math,
            num_with_ref,
            excel_zahl(fres_index),
            fres_total_syllables,
            fres_total_words,
            fres_total_sentence
        ])

    ######################################################################
    ######### Ausgabe der Artikeldatei fuer weitere Auswertungen #########
    ######################################################################

    file_name = "ergebnisse_artikel_crd_crr_" + str(year) + ".csv"

    with open(file_name, "w", newline="", encoding="utf-8-sig") as outfile:
        writer = csv.writer(outfile, delimiter=";")

        writer.writerow([
            "article",
            "weighted_regulatory_operators",
            "unweighted_regulatory_operators",
            "operators_total",
            "fres",
            "sentences",
            "words",
            "syllables",
            "words_per_sentence",
            "syllables_per_word",
            "number_internal_references",
            "complexity_with_references",
            "clump_size"
        ])

        for i in range(len(ParagraphList)):
            # Kontrollgroessen fuer die FRES-Berechnung des aktuellen Artikels.
            if NumParaSent[i] > 0:
                words_per_sentence = NumParaWords[i] / NumParaSent[i]
            else:
                words_per_sentence = 0

            if NumParaWords[i] > 0:
                syllables_per_word = NumParaSylla[i] / NumParaWords[i]
            else:
                syllables_per_word = 0

            writer.writerow([
                ParagraphList[i],
                Reg_Operators_per_Paragraph[i],
                Reg_Operators_alone[i],
                Operators_per_Paragraph[i],
                excel_zahl(FRESPara[i]),
                NumParaSent[i],
                NumParaWords[i],
                NumParaSylla[i],
                excel_zahl(words_per_sentence),
                excel_zahl(syllables_per_word),
                len(ParagraphVerweise[i]),
                excel_zahl(reg_costs_vreg[i]),
                len(Klumpenparagraph[i])
            ])

    ######################################################################
    ######### Ausgabe der dot-Datei fuer den Verweisgraphen ##############
    ######################################################################

    file_name = "graph_crd_crr_" + str(year) + ".dot"

    with open(file_name, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile, delimiter=";", escapechar=" ", quoting=csv.QUOTE_NONE)

        writer.writerow(["digraph G  {"])
        writer.writerow(["fontname=\"Helvetica,Arial,sans-serif\""])
        writer.writerow(["node [fontname=\"Helvetica,Arial,sans-serif\"]"])
        writer.writerow(["edge [fontname=\"Helvetica,Arial,sans-serif\"]"])
        writer.writerow(["layout=neato"])
        writer.writerow(["center=\"\""])
        writer.writerow(["node[width=.25,height=.375,fontsize=9]"])

        # Zeichnen der Kanten, also der internen Verweise.
        for i_ in range(len(ParagraphList)):
            for j_ in range(len(ParagraphVerweise[i_])):
                try:
                    v = ParagraphList.index(ParagraphVerweise[i_][j_])
                    line_text = "\"" + ParagraphList[i_] + "\"" + "->" + "\"" + ParagraphList[v] + "\"" + ";"
                    writer.writerow([line_text])
                except:
                    pass

        # Zeichnen der Knoten, also der Artikel.
        for para_ in ParagraphList:
            line_text = "\"" + para_ + "\"" + "[label=\"\",shape=circle,height=0.12,width=0.12,fontsize=1];"
            writer.writerow([line_text])

        writer.writerow(["}"])

    ######################################################################
