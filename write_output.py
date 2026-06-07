''' Version: 30.04.2026
Funktion zur Ausgabe der Ergebnisse
'''

import csv

def write_output(year,exp_ref_factor,ParagraphList,ParagraphVerweise,number_verweise,counter_missing,Operators_per_Paragraph,Klumpenparagraph,num_para,counter_cycl_compl,counter_quantity,counter_math,
sum_reg_costs_vreg,num_with_ref,fres_index,fres_total_syllables,fres_total_words,fres_total_sentence):
    
    with open('U:/Dokumente/Daten/SEC_Regulatorik/ReguCost'+ str(exp_ref_factor) +'.csv') as readfile:
        reader = csv.reader(readfile.readlines(), delimiter=';')

    index_year = year - 1970 + 1

    with open('U:/Dokumente/Daten/SEC_Regulatorik/ReguCost'+ str(exp_ref_factor) +'.csv', 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=';')
        counter = 0
        for line in reader:
            if counter == index_year:
                writer.writerow((year, len(ParagraphList), number_verweise, counter_missing,
                                     sum(Operators_per_Paragraph),sum_reg_costs_vreg,
                                     max([len(Klumpenparagraph[i])] for i in range(num_para))[0],
                                     counter_cycl_compl, counter_quantity,
                                     counter_math,num_with_ref,fres_index,fres_total_syllables,fres_total_words,
                                     fres_total_sentence))             
            else:
                writer.writerow(line)
            counter += 1
    #    writer.writerows(reader)
    
    ######################################################################
    ######### Ausgabe der dot-Dateneien fuer die Graphen #################
    file_name = "U:/Dokumente/Daten/SEC_Regulatorik/SEC_Graphen/SEC_Graph_"+str(year)+".txt" # Filename
    with open(file_name, 'w', newline='') as outfile:
            writer = csv.writer(outfile, delimiter=';',escapechar=' ',quoting = csv.QUOTE_NONE)
            writer.writerow(["digraph G  {"])
            writer.writerow(["fontname=\"Helvetica,Arial,sans-serif\""])
            writer.writerow((["node [fontname=\"Helvetica,Arial,sans-serif\"]"]))
            writer.writerow((["edge [fontname=\"Helvetica,Arial,sans-serif\"]"]))
            writer.writerow((["layout=neato"]))
            writer.writerow((["center=\"\""]))
            writer.writerow((["node[width=.25,height=.375,fontsize=9]"]))
            # Zeichnen der Kanten (Verweise)
            for i_ in range(len(ParagraphList)):
                for j_ in range(len(ParagraphVerweise[i_])):
                    try:
                        v = ParagraphList.index((ParagraphVerweise[i_])[j_]) 
                        line_text = ParagraphList[i_] + "->" + ParagraphList[v] + ";"
                        writer.writerow(([line_text]))
                    except:
                        pass
            # Zeichnen der Knoten (Paragraphen)
            for para_ in ParagraphList:
                line_text = para_ + "[label=\"\",shape=circle,height=0.12,width=0.12,fontsize=1];"
                writer.writerow(([line_text]))
                
                
            writer.writerow(("}"))
    ######################################################################
    
    