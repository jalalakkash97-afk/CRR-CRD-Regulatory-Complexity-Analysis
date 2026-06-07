''' Version: 27.04.2026
Funktion zur weiteren Analyse des Klumpens
'''

import numpy as np
import copy

def clumb_analysis(ParagraphList,Klumpenparagraph,ParagraphVerweiseKlumpen,ParagraphRegOperatorenKlumpenKosten,ParagraphImplicitVerweiseKlumpen,reg_costs_vreg,reg_costs_no_fres,num_para):
    
    ########## Identifizierung des groesten Klumpen:
    index_great_clumb = 0
    size_great_clumb = 0
    
    for index_i in range(len(Klumpenparagraph)):
        #print(len(Klumpenparagraph[index_i]))
        if len(Klumpenparagraph[index_i]) > size_great_clumb:
            index_great_clumb = index_i
            size_great_clumb = len(Klumpenparagraph[index_i])            
    
    cost_great_clump_alone = ParagraphRegOperatorenKlumpenKosten[index_great_clumb]
    cost_great_clump = reg_costs_vreg[index_great_clumb]
    no_fres_great_clump = reg_costs_no_fres[index_great_clumb]
    
    indicator_cite_clumb = [False for index_i in range(len(Klumpenparagraph))]
    sum_implizit_ref_clump = 0
    for index_i in range(len(Klumpenparagraph)):
        # if index_i == index_great_clumb:
            # print(ParagraphImplicitVerweiseKlumpen[index_i])
            # print(ParagraphList)
        if (index_i != min(Klumpenparagraph[index_i])):
            continue
        for v_name in ParagraphImplicitVerweiseKlumpen[index_i]:
            #if v_name == '210.3-07':
                #print("test???")
                #v = ParagraphList.index(v_name)
            try:
                v = ParagraphList.index(v_name)
                #print("test,","i:",index_i,", v:",v)
                try:
                    #print("Test: passt bisher zumindest")
                    w = Klumpenparagraph[v].index(index_great_clumb)
                    #print("Test: passt eigentlich")
                    sum_implizit_ref_clump += 1
                    indicator_cite_clumb[index_i] = True
                    break
                except:
                    pass
            except:
                pass
    
    sum_explizit_ref_clump = 0
    for index_i in range(len(Klumpenparagraph)):
        # if index_i == index_great_clumb:
            # print(ParagraphImplicitVerweiseKlumpen[index_i])
            # print(ParagraphList)
        if (index_i != min(Klumpenparagraph[index_i])):
            continue
        for v_name in ParagraphVerweiseKlumpen[index_i]:
            #if v_name == '210.3-07':
                #print("test???")
                #v = ParagraphList.index(v_name)
            try:
                v = ParagraphList.index(v_name)
                #print("test,","i:",index_i,", v:",v)
                try:
                    #print("Test: passt bisher zumindest")
                    w = Klumpenparagraph[v].index(index_great_clumb)
                    #print("Test: passt eigentlich")
                    sum_explizit_ref_clump += 1
                    break
                except:
                    pass
            except:
                pass
    
    ################################################################################
    ################################################################################
    # Analyse der Verweisstruktur auf Klumpenniveau "oberhalb" des größten Klumpens    
    number_nodes_over_clumb = sum(indicator_cite_clumb)
    averg_ref_over_clumb = 0
    denom_number_notes = 0
    averg_oper_over_clumb = 0
    ref_over_clumb_array = []
    
    for index_i in range(len(Klumpenparagraph)):
        clumb_root = min(Klumpenparagraph[index_i])
        if (indicator_cite_clumb[clumb_root]) and clumb_root == index_i:
            ref_counter = 0
            #free_Klumpen_refs = copy.deepcopy(indicator_cite_clumb)
            free_Klumpen_refs = [False for i_ in range(len(Klumpenparagraph))]
            for index_v in range(len(Klumpenparagraph)):
                if indicator_cite_clumb[index_v]:
                    for i_ in Klumpenparagraph[index_v]:
                       free_Klumpen_refs[index_v] = True 
                    #free_Klumpen_refs[index_v] = True
            #free_Klumpen_refs[index_great_clumb] = False
            for index_v in Klumpenparagraph[index_great_clumb]:
                free_Klumpen_refs[index_v] = False
            #free_Klumpen_refs[index_i] = False
            for index_v in Klumpenparagraph[index_i]:
                free_Klumpen_refs[index_v] = False
            
            #averg_ref_over_clumb += (len(Klumpenparagraph[index_i]-1)
            denom_number_notes += 1
            
            averg_oper_over_clumb += reg_costs_no_fres[index_i]
            
            for v_name in ParagraphVerweiseKlumpen[index_i]:
                try:
                    v = ParagraphList.index(v_name)
                    #u = min(Klumpenparagraph[v])
                    if free_Klumpen_refs[v]:
                        ref_counter += 1
                        averg_ref_over_clumb += 1
                        for index_w in Klumpenparagraph[index_v]:
                            free_Klumpen_refs[index_v] = False
                except:
                    pass
            ref_over_clumb_array.append(ref_counter)
    
    averg_ref_over_clumb = averg_ref_over_clumb/denom_number_notes
    averg_oper_over_clumb = averg_oper_over_clumb/number_nodes_over_clumb
    median_ref_over_clumb = np.median(ref_over_clumb_array)
    ################################################################################
    ################################################################################
    
    ################################################################################
    ### Bestimmung der Laenge der (gewichteten Verweisketten) ueber dem Klumpen ####
    ################################################################################
    f_equal_weight = [-1 for i in range(num_para)]
    f_weighted = [-1 for i in range(num_para)]
    leafs_below = [1 for i in range(num_para)]
    clumb_counter = 0
    max_clumb = 1
    
    top_nodes_index = [0 for i in range(num_para)]
    for i in range(num_para):
        if indicator_cite_clumb[i]:
            top_nodes_index[i] = 1
    
    for i in range(num_para):
        #print("Kontrollpunkt -1!")
        if f_equal_weight[i] != -1 or (indicator_cite_clumb[i]==False) or (min(Klumpenparagraph[i])!=i):
            continue
        #print("Kontrollpunkt 0!")
        Q = [i]
        while len(Q) > 0:
            #print(Q)
            u = Q.pop()
            #print(Q)
            stop_ = False
            for v_name in ParagraphVerweiseKlumpen[u]:
                try:
                    w = ParagraphList.index(v_name)
                    v = min(Klumpenparagraph[w])
                except:
                    continue
                #print("Kontrollpunkt 1!")
                if u == v:
                    continue
                if f_equal_weight[v] == -1 and indicator_cite_clumb[v]:
                    #print("Kontrollpunkt 2!")
                    Q.append(u)
                    Q.append(v)
                    stop_ = True
                    break
                    
            if stop_ == False:
                #print("Test:",clumb_counter,number_nodes_over_clumb,Q)
                f_equal_weight[u] = 0 #1+len(Klumpenparagraph[u]/2
                f_weighted[u] = 0 # 1+len(Klumpenparagraph[u]/2
                leafs_below[u] = 0
                direct_childs = 0
                
                
                free_Klumpen_refs = copy.deepcopy(indicator_cite_clumb)
                free_Klumpen_refs[u] = False
                for v_name in ParagraphVerweiseKlumpen[u]:
                    try:
                        w = ParagraphList.index(v_name)
                        v = min(Klumpenparagraph[w])
                        #print("Kontrollpunkt 4!")
                        if free_Klumpen_refs[v]:
                            #print("Kontrollpunkt 5!")
                            f_equal_weight[u] += f_equal_weight[v]
                            direct_childs += 1
                            f_weighted[u] += f_weighted[v]*leafs_below[v]
                            leafs_below[u] += leafs_below[v]
                            
                            free_Klumpen_refs[v] = False
                            top_nodes_index[v] = 0
                            
                    except:
                        continue
                if leafs_below[u] == 0:
                    leafs_below[u] = 1
                        
                f_equal_weight[u] = f_equal_weight[u]/max([direct_childs,1]) + 1 +(len(Klumpenparagraph[u])-1)
                f_weighted[u] = f_weighted[u]/max([leafs_below[u],1]) + 1 + (len(Klumpenparagraph[u])-1)
                #print("Sind zumindest bis hierhin gekommen!")
                
                if len(Klumpenparagraph[u]) > 1:
                    clumb_counter += 1
                if max_clumb < len(Klumpenparagraph[u]):
                    max_clumb = len(Klumpenparagraph[u])
    
    
    
    print("Knoten über Klumpen:", number_nodes_over_clumb)
    print("Klumpen davon:", clumb_counter)
    print("Maximaler Klumpen:", max_clumb)
    
    # for i in range(num_para):
        # if indicator_cite_clumb[i]:
            # print(i,f_equal_weight[i],f_weighted[i],leafs_below[i],top_nodes_index[i])
    
    f_equal_weight_sum = 0
    f_weighted_sum = 0
    leafs_below_sum = 0
    top_nodes_sum = 0
    seperated_nodes_sum = 0
    ref_over_clumb_array2 = []
    counter = 0
    
    for i in range(num_para):
        if top_nodes_index[i]==1 and f_weighted[i] > 1:
           f_equal_weight_sum += f_equal_weight[i]
           top_nodes_sum += 1
           f_weighted_sum += f_weighted[i]*leafs_below[i]
           leafs_below_sum += leafs_below[i]
           ref_over_clumb_array2.append(ref_over_clumb_array[counter])
           counter += 1
        if top_nodes_index[i]==1 and f_weighted[i] == 1:
            seperated_nodes_sum += 1
    
    
    if top_nodes_sum == 0:
        top_nodes_sum = 1
        leafs_below_sum = 1
        f_equal_weight_sum = f_equal_weight_sum 
        f_weighted_sum = f_weighted_sum
        median_ref_over_clumb = 0
        averg_ref_over_clumb = 0
    else:    
        f_equal_weight_sum = f_equal_weight_sum/top_nodes_sum
        f_weighted_sum = f_weighted_sum/leafs_below_sum
        median_ref_over_clumb = np.median(ref_over_clumb_array2)
        averg_ref_over_clumb = averg_ref_over_clumb*denom_number_notes/(denom_number_notes-seperated_nodes_sum)
    
    
    print("Median Kanten:",median_ref_over_clumb,"Mean Kanten:",averg_ref_over_clumb)
    print("f gleichgewichtet (mean, max):",f_equal_weight_sum,max(f_equal_weight))
    print("f leafs gewichtet (mean, max)::",f_weighted_sum,max(f_weighted))
    print("Separate Klumpen:", seperated_nodes_sum)
    print("")
    print("")
    
    
    
    
    
    
    return (cost_great_clump_alone,cost_great_clump,sum_implizit_ref_clump,no_fres_great_clump,sum_explizit_ref_clump,averg_oper_over_clumb,averg_ref_over_clumb,number_nodes_over_clumb,
            f_equal_weight_sum,f_equal_weight,f_weighted_sum,f_weighted,top_nodes_sum)