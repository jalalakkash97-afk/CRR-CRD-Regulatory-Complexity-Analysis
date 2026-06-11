'''Funktion zur Bestimmung der relevanten Statistiken fuer CRD und CRR.'''

from operator_counting import operator_counting


def compute_statistics_crd_crr(
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
):
    # Berechnet die Gesamtkomplexitaet ueber alle eindeutigen Klumpen.
    sum_reg_costs_vreg = 0

    # Zaehlt die Klumpen mit mehr als einem Artikel.
    num_great_lump = 0

    # Geht alle Artikel durch.
    for u in range(num_para):
        # Der kleinste Index im Klumpen ist der eindeutige Vertreter.
        nodes = Klumpenparagraph[u]
        nodes.sort()

        # Jeder Klumpen wird nur einmal gezaehlt.
        if nodes[0] == u:
            # Wie im Original: Komplexitaet des Klumpens mal Anzahl der enthaltenen Artikel.
            sum_reg_costs_vreg += reg_costs_vreg[u] * len(Klumpenparagraph[u])

            # Merkt sich, ob es ein Mehrartikel-Klumpen ist.
            num_great_lump += int(len(Klumpenparagraph[u]) > 1)

    # Zaehlt logische Operatoren in CRD und CRR.
    Log_Operators_CRD = operator_counting(
        log_operators,
        ParagraphList_CRD,
        PositionsParagraph_CRD,
        EndParagraph_CRD,
        CRD_Text
    )
    Log_Operators_CRR = operator_counting(
        log_operators,
        ParagraphList_CRR,
        PositionsParagraph_CRR,
        EndParagraph_CRR,
        CRR_Text
    )
    counter_cycl_compl = sum(Log_Operators_CRD) + sum(Log_Operators_CRR)

    # Zaehlt regulatorische Operatoren in CRD und CRR.
    Reg_Operators_CRD = operator_counting(
        reg_operators,
        ParagraphList_CRD,
        PositionsParagraph_CRD,
        EndParagraph_CRD,
        CRD_Text
    )
    Reg_Operators_CRR = operator_counting(
        reg_operators,
        ParagraphList_CRR,
        PositionsParagraph_CRR,
        EndParagraph_CRR,
        CRR_Text
    )
    counter_quantity = sum(Reg_Operators_CRD) + sum(Reg_Operators_CRR)

    # Zaehlt mathematische Operatoren in CRD und CRR.
    Math_Operators_CRD = operator_counting(
        math_operators,
        ParagraphList_CRD,
        PositionsParagraph_CRD,
        EndParagraph_CRD,
        CRD_Text
    )
    Math_Operators_CRR = operator_counting(
        math_operators,
        ParagraphList_CRR,
        PositionsParagraph_CRR,
        EndParagraph_CRR,
        CRR_Text
    )
    counter_math = sum(Math_Operators_CRD) + sum(Math_Operators_CRR)

    # Bestimmt die Anzahl der Artikel mit mindestens einem internen Verweis.
    num_with_ref = 0
    for i in range(len(ParagraphList)):
        if len(ParagraphVerweise[i]) > 0:
            num_with_ref += 1

    # Berechnet den FRES-Gesamtwert fuer den gemeinsamen CRD/CRR-Korpus.
    fres_total_sentence = sum(NumParaSent)
    fres_total_words = sum(NumParaWords)
    fres_total_syllables = sum(NumParaSylla)

    if fres_total_sentence > 0 and fres_total_words > 0:
        fres_index = (
            206.835
            - 1.015 * (fres_total_words / fres_total_sentence)
            - 84.6 * (fres_total_syllables / fres_total_words)
        )
    else:
        fres_index = 0

    return (
        sum_reg_costs_vreg,
        num_great_lump,
        counter_cycl_compl,
        counter_quantity,
        counter_math,
        num_with_ref,
        fres_index,
        fres_total_syllables,
        fres_total_words,
        fres_total_sentence
    )
