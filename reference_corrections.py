'''Version: 23.04.2026
Funktion, die Name von Verweisen notfalls korrigiert und die Verweise sortiert 
'''

import numpy as np
from functools import cmp_to_key
import copy

from index_verweis import index_verweise

def reference_corrections(ParagraphVerweise,ParagraphList):

    # Testen, ob alle vorhanden?
    counter_missing = 0
    for counter_outer in range(len(ParagraphVerweise)):
        Verweise = ParagraphVerweise[counter_outer]
        for counter_inner in range(len(Verweise)):
            x = Verweise[counter_inner]
            if x in ParagraphList:
                continue
            else:
                ################## Nameskorrektur ###########################
                # O -> 0
                # I,l -> 1
                # Z -> 2
                #
                #
                # S -> 5
                #
                #
                # B -> 8
                #
                # \t entfernen und eventuell Namensrest abschneiden
                # — -> -
                # , -> .
                start_ = 0
                while True:
                    try:
                        tabposition = x.index("\t", start_)
                        nextletter = x[(tabposition + 1)]
                        start_ = tabposition + 1
                        if (nextletter.isnumeric() == False):
                            x = x[0:tabposition]
                    except:
                        break
                x = x.replace('\t', '')
                x = x.replace('O', '0')
                x = x.replace('I', '1')
                x = x.replace('l', '1')
                x = x.replace('!', '1')
                x = x.replace('Z', '2')
                x = x.replace('S', '5')
                x = x.replace('B', '8')
                x = x.replace('—', '-')
                x = x.replace(',', '.')
                x = x.replace('^', '-')
                x = x.replace('C', 'c')

                x = x.replace("\n", "")
                len_x = len(x)
                is_found = False
                for i in range(0, len_x):
                    y = x[0:(len_x - i)]
                    if y in ParagraphList:
                        Verweise[counter_inner] = y
                        is_found = True
                        break
                if is_found == False:
                    counter_missing += 1
                    #print("Warnung nicht verifizierter Verweis: ", x)
        if len(Verweise) > 0:
            Verweise2 = [(Verweise[i], index_verweise(Verweise[i], ParagraphList)) for i in range(len(Verweise))]
            Verweise2 = sorted(Verweise2, key=lambda x: x[1])
            Verweise = [Verweise2[0][0]]
            for index_ in range(1, len(Verweise2)):
                if Verweise2[index_][0] != Verweise2[(index_ - 1)][0]:
                    Verweise.append(Verweise2[index_][0])
            try:
                Verweise.remove(ParagraphList[counter_outer])
            except:
                pass
        ParagraphVerweise[counter_outer] = Verweise


    return (ParagraphVerweise,counter_missing)