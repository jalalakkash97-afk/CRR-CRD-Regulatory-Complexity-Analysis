'''Version: 27.04.2026
Funktion zur Kontraktion eines Zirkels

'''

from index_verweis import index_verweise
from factors import verweis_factor_fun
from factors import zirkel_factor_fun



def zirkelkontraktion(nodes, Klumpenpara, ParaVerweiseKlumpen, ParaImplicitVerweiseKlumpen, ParaOperatorenKlumpen, ParaRegOperatorenKlumpen, ParagraphList,exp_ref_factor):
        # nodes: Indizes der Paragraphen des gefundenen Zirkels
        # Klumpenpara: Zirkelpara[i] entält die Indizes der Paragraphen, die zum selben Klumben wir Paragraph i gehören
        # ParaVerweiseKlumpen: ParaVerweiseKlumpen[i] enthält alle Verweise des Klumpens, die zum selben Klumpen
        #                      wie Paragraph i gehören
        # ParaImplicitVerweiseKlumpen: ParaImplicitVerweiseKlumpen[i] enthält alle impliziten Verweise des Klumpens, die zum selben Klumpen
        #                      wie Paragraph i gehören
        # ParaOperatorenKlumpen: ParaOperatorenKlumpen[i] enthält kumulierte Operatoren des Klumpen von Paragraph i
        # ParaRegOperatorenKlumpen: ParaRegOperatorenKlumpen[i] enthält kumulierte regul. Operatoren des Klumpen von Paragraph i
        # OperatorsPara: OperatorsPara[i] ist Anzahl an Operatoren in Paragraph i
        # ParaVerweise: ParaVerweise[i] enthält die Verweise des Paragraphs i
        # ParagraphList: Array mit den "Namen" der Paragraphen

        # Für alle Knoten des gefundenen Zirkels müssen die zugehörigen Klumpen zusammengelegt werden
        # und der Klumpen muss kontrahiert werden
        neuer_klumpen = []
        Verweise = []
        ImplicitVerweis = []
        operator_ = 0
        reg_operator_ = 0
        
        
        for v in nodes:
            neuer_klumpen += Klumpenpara[v]
            Verweise += ParaVerweiseKlumpen[v]
            ImplicitVerweis += ParaImplicitVerweiseKlumpen[v]
            #operator_ += ParaOperatorenKlumpen[v]/zirkel_factor_fun(exp_ref_factor,len(Klumpenpara[v]))
            reg_operator_ += ParaRegOperatorenKlumpen[v] / zirkel_factor_fun(exp_ref_factor, len(Klumpenpara[v]))
            
            
            #*2/(len(Klumpenpara[v])+1)
        neuer_klumpen = sorted(set(neuer_klumpen))
        operator_ = operator_*zirkel_factor_fun(exp_ref_factor,len(neuer_klumpen))#(len(neuer_klumpen)+1)/2
        reg_operator_ = reg_operator_ * zirkel_factor_fun(exp_ref_factor, len(neuer_klumpen))  # (len(neuer_klumpen)+1)/2

        # sortiere Verweise und mache sie unique
        if len(Verweise) > 0:
            Verweise2 = [(Verweise[i], index_verweise(Verweise[i], ParagraphList)) for i in range(len(Verweise))]
            Verweise2 = sorted(Verweise2, key=lambda x: x[1])
            Verweise = list(set([Verweise2[i][0] for i in range(len(Verweise2))]))

        # Löschen aller Knoten des Klumpens aus den Verweisen
        for v in neuer_klumpen:
            v_name = ParagraphList[v]
            try:
                Verweise.remove(v_name)
                continue
            except:
                continue

        # sortiere ImplicitVerweise und mache sie unique
        if len(ImplicitVerweis) > 0:
            ImplicitVerweis2 = [(ImplicitVerweis[i], index_verweise(ImplicitVerweis[i], ParagraphList)) for i in
                                 range(len(ImplicitVerweis))]
            ImplicitVerweis2 = sorted(ImplicitVerweis2, key=lambda x: x[1])
            ImplicitVerweis = list(set([ImplicitVerweis2[i][0] for i in range(len(ImplicitVerweis2))]))

        # Löschen aller Knoten des Klumpens aus den Verweisen
        for v in neuer_klumpen:
            v_name = ParagraphList[v]
            try:
                ImplicitVerweis.remove(v_name)
                continue
            except:
                continue

        # Kontrahiere neuen entstandenen Klumpen:
        for v in neuer_klumpen:
            Klumpenpara[v] = neuer_klumpen
            ParaVerweiseKlumpen[v] = Verweise
            ParaImplicitVerweiseKlumpen[v] = ImplicitVerweis
            ParaOperatorenKlumpen[v] = operator_
            ParaRegOperatorenKlumpen[v] = reg_operator_
            
            
        # Kontrolle:
        test_sum_reg = 0
        for i_ in range(len(ParagraphList)):
            w = min(Klumpenpara[i_])
            if i_ == w:
                test_sum_reg += ParaRegOperatorenKlumpen[w]
        
        #if (test_sum_reg != sum_reg_oper):
        #    print("Fehler: Kontraktion macht etwas falsch!!!")
        #else:
        #    print("Kontraktion passt")

        return (Klumpenpara, ParaOperatorenKlumpen, ParaRegOperatorenKlumpen, ParaVerweiseKlumpen, ParaImplicitVerweiseKlumpen)
