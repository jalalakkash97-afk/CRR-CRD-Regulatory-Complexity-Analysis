''' Version: 27.04.2026
Funktion zur Bestimmung der relevanten Statistiken (Quantitiy, FRES, Gesamtkosten)


'''


def compute_statistics(ParagraphList,ParagraphVerweise,PositionsParagraph,EndParagraph,Klumpenparagraph,log_operators,reg_operators,math_operators,CFR_Text,NumParaSent,
NumParaWords,NumParaSylla,num_para,reg_costs_vreg):
    
    
    
    ############ Komplexitaet nach unserem Maß fuer den gesamten Text ###############
    sum_reg_costs_vreg = 0
    num_great_lump = 0
    for u in range(num_para):
        nodes = Klumpenparagraph[u]
        nodes.sort()
        if nodes[0] == u:
            sum_reg_costs_vreg += (reg_costs_vreg[u] * len(Klumpenparagraph[u]))
            num_great_lump += int(len(Klumpenparagraph[u]) > 1)
    
    
    #################### Menge logischer Operatoren ################
    counter_cycl_compl = 0
    for i in range(len(ParagraphList)):
        # if i%100 ==0:
        #    print(i)
        #counter = 0
        parabegin = PositionsParagraph[i]
        paraend = EndParagraph[i]
        for operator_ in log_operators:
            # print(operator_)
            currentposition = parabegin
            while True:
                try:
                    currentposition = CFR_Text.index(operator_, (currentposition + 1), paraend)
                    counter_cycl_compl += 1
                except:
                    break
        

    
    ############## Menge regulatorischer Operatoren ###############
    counter_quantity = 0
    for i in range(len(ParagraphList)):
        # if i%100 ==0:
        #    print(i)
        #counter = 0
        parabegin = PositionsParagraph[i]
        paraend = EndParagraph[i]
        for operator_ in reg_operators:
            # print(operator_)
            currentposition = parabegin
            while True:
                try:
                    currentposition = CFR_Text.index(operator_, (currentposition + 1), paraend)
                    counter_quantity += 1
                except:
                    break
    
    ############## Menge mathematischer Operatoren ###############
    counter_math = 0
    for i in range(len(ParagraphList)):
        # if i%100 ==0:
        #    print(i)
        #counter = 0
        parabegin = PositionsParagraph[i]
        paraend = EndParagraph[i]
        for operator_ in math_operators:
            # print(operator_)
            currentposition = parabegin
            while True:
                try:
                    currentposition = CFR_Text.index(operator_, (currentposition + 1), paraend)
                    counter_math += 1
                except:
                    break
    


    # Bestimmen der Anzahl an Paragraphen mit Verweisen:
    num_with_ref = 0
    for i in range(len(ParagraphList)):
        if (len(ParagraphVerweise[i]) > 0 ):
            num_with_ref += 1
            
            
    ########## Flesch-Kincaid reading ease score (FRES) #######
    fres_total_sentence = sum(NumParaSent)
    fres_total_words = sum(NumParaWords)
    fres_total_syllables = sum(NumParaSylla)
    fres_index = 206.835 - 1.015*(fres_total_words/fres_total_sentence) - 84.6*(fres_total_syllables/fres_total_words)
    
    return (sum_reg_costs_vreg,num_great_lump,counter_cycl_compl, counter_quantity,counter_math,num_with_ref,fres_index,fres_total_syllables,fres_total_words,fres_total_sentence)