''' Version: 27.04.2026
funktion zum Bestimmen des der Komplexitaet fuer die einzelnen Paragraphen des Graphen

'''
import numpy as np
import copy

from factors import verweis_factor_fun
from factors import zirkel_factor_fun
from contraction import zirkelkontraktion
from index_verweis import index_verweise


def compute_complexity(ParagraphList,ParagraphVerweise,Operators_per_Paragraph,Reg_Operators_per_Paragraph,Reg_Operators_alone,num_para,sum_reg_oper,undef_ref_costs,exp_ref_factor,clumb_factor):
    
    
    # Initialisiere ohne gefundene Zirkel:
    Klumpenparagraph = [[i] for i in range(num_para)]
    ParagraphVerweiseKlumpen = copy.deepcopy(ParagraphVerweise)
    ParagraphImplicitVerweiseKlumpen = copy.deepcopy(ParagraphVerweise)
    #MaxVerweisKette = [0 for i in range(num_para)]
    ParagraphOperatorenKlumpen = copy.deepcopy(Operators_per_Paragraph)
    ParagraphRegOperatorenKlumpen = copy.deepcopy(Reg_Operators_per_Paragraph)
    
    
    
    
    
    
    reg_costs_vreg = [-1 for i in range(num_para)]
    
    
    
    if (sum(reg_costs_vreg) > num_para*sum_reg_oper):
        print("Fehler: Regulatorische Kosten übersteigen obere Schranke")

    zirkelschluss = False

    for i in range(num_para):
        #if i % 10 == 0:
            #print("Aeussere Schleife:", i)
        if reg_costs_vreg[i] != -1:
            continue
        Q = [i]
        while len(Q) > 0:
            # print("Q", Q)
            u = Q.pop()
            stop_ = False
            zirkelschluss = False
            # if u == 228:
            # print(ParagraphVerweiseKlumpen[u])
            for v_name in ParagraphVerweiseKlumpen[u]:
                try:
                    v = ParagraphList.index(v_name)
                except:
                    continue
                if u == v:
                    continue
                if reg_costs_vreg[v] == -1:
                    Q.append(u)
                    if v in Q:
                        # print("Zirkelschluss")
                        ########### Kontrahiere den gefundenen Zirkel zu einem Knoten ############
                        zirkel_start_index = Q.index(v)


                        nodes = [Q[index_] for index_ in range(zirkel_start_index, len(Q))]
                        # print("Nodes des Zirkels: ", nodes)
                        (Klumpenparagraph, ParagraphOperatorenKlumpen, ParagraphRegOperatorenKlumpen, ParagraphVerweiseKlumpen, ParagraphImplicitVerweiseKlumpen) = \
                            zirkelkontraktion(nodes, Klumpenparagraph, ParagraphVerweiseKlumpen, ParagraphImplicitVerweiseKlumpen, ParagraphOperatorenKlumpen, ParagraphRegOperatorenKlumpen, ParagraphList,exp_ref_factor)
                        Q = [i]
                        zirkelschluss = True
                        break

                    else:
                        Q.append(v)
                        stop_ = True
                        break
            if zirkelschluss == True:
                continue
            elif stop_ == False:
                #print("Stand:",Klumpenparagraph[u])
                reg_costs_vreg[u] = ParagraphRegOperatorenKlumpen[u]
                
                
                if (reg_costs_vreg[u] > sum_reg_oper and ParagraphList[u] == "222.72"):
                    #pass
                    print("Fehler: Regulatorische Kosten übersteigen obere Schranke, bei Paragraph: ", ParagraphList[u], "schon bei Initialisierung!!!")
                #if (sum(reg_costs_vreg) > num_para*sum_reg_oper):
                #    print("Fehler: Regulatorische Kosten übersteigen obere Schranke, bei Paragraph: " ParagraphList[u])
                allredy_implicit_seen_nodes = [min(Klumpenparagraph[u])]
                #print('Neuer Knoten: ', u)
                #print(ParagraphImplicitVerweiseKlumpen[u])
                
                
                #reg_costs[u] = 0
                #reg_costs_vreg[u] = 0
                all_implicit_ref = [] #copy.deepcopy(Klumpenparagraph[u])
                all_explicit_ref = []
                num_unrecg_ref = 0
                for v_name in ParagraphVerweiseKlumpen[u]:
                    try:
                        v = ParagraphList.index(v_name)
                        #w = min(Klumpenparagraph[v])
                        all_explicit_ref += Klumpenparagraph[v]
                        all_implicit_ref += Klumpenparagraph[v]
                        for z_name in ParagraphImplicitVerweiseKlumpen[v]:
                            try:
                                z = ParagraphList.index(z_name)
                                all_implicit_ref += Klumpenparagraph[z]
                            except:
                                pass
                    except:
                        num_unrecg_ref += 1
                all_implicit_ref = list(set(all_implicit_ref))
                
                
                #### Entscheidung, ob Komplexitaet von Paragraphen innerhalb der Rekursion mehrfach gezaehlt werden soll (z.B. bei einem gewurzelten Baum, ob Wurzel dann mehrfach zaehlen soll):
                ALL_REF_COUNTER = True
                
                if ALL_REF_COUNTER:
                    for v in all_explicit_ref:
                        if v == min(Klumpenparagraph[v]):
                            reg_costs_vreg[u] += reg_costs_vreg[v] * verweis_factor_fun(exp_ref_factor, len(
                                Klumpenparagraph[u]))                              
                            if v != u:
                                ParagraphImplicitVerweiseKlumpen[u].extend(ParagraphImplicitVerweiseKlumpen[v])
                else:
                    for v in all_implicit_ref:                
                        if v == min(Klumpenparagraph[v]):
                            reg_costs_vreg[u] += ParagraphRegOperatorenKlumpen[v] * verweis_factor_fun(exp_ref_factor, len(
                                Klumpenparagraph[u]))
                                                            
                            if v != u:
                                ParagraphImplicitVerweiseKlumpen[u].extend(ParagraphImplicitVerweiseKlumpen[v])
                
                
                
                reg_costs_vreg[u] += num_unrecg_ref*undef_ref_costs
                
                    
                # sortiere ImplicitVerweise und mache sie unique
                if len(ParagraphImplicitVerweiseKlumpen[u]) > 0:
                    ImplicitVerweis = ParagraphImplicitVerweiseKlumpen[u]
                    ImplicitVerweis2 = [(ImplicitVerweis[i], index_verweise(ImplicitVerweis[i], ParagraphList))
                                                for i in
                                                range(len(ImplicitVerweis))]
                    ImplicitVerweis2 = sorted(ImplicitVerweis2, key=lambda x: x[1])
                    #print([ImplicitVerweis2[i][0] for i in range(len(ImplicitVerweis2))])
                    ParagraphImplicitVerweiseKlumpen[u] = list(set([ImplicitVerweis2[i][0] for i in range(len(ImplicitVerweis2))]))
                
                
                # Schleife, um die Kosten fuer die restlichen Knoten des gleichen Klumpen auch festzuschreiben:
                for v in Klumpenparagraph[u]:                    
                    reg_costs_vreg[v] = reg_costs_vreg[u]                   
                    if (reg_costs_vreg[u] > sum_reg_oper):
                        pass
                        #print("Fehler: Regulatorische Kosten übersteigen obere Schranke, bei anderem Paragraph: ", ParagraphList[v])
                # Schleife, um die impliziten Verweise der restlichen Knoten des gleichen Klumpen zu aktualisieren:
                for v in Klumpenparagraph[u]:
                    ParagraphImplicitVerweiseKlumpen[v] = ParagraphImplicitVerweiseKlumpen[u]

                

        if zirkelschluss == True:
            break
    
    
    return (Klumpenparagraph, ParagraphVerweiseKlumpen, ParagraphImplicitVerweiseKlumpen, ParagraphOperatorenKlumpen, ParagraphRegOperatorenKlumpen,  reg_costs_vreg)
    
