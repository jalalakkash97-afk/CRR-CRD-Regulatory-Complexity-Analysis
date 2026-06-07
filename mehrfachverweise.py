''' Version: 22.04.2026
Funktion zur Identifizierung und Auswertung von Mehrfachverweisen im Text
'''

import numpy as np
from functools import cmp_to_key
import copy

def mehrfachverweise(ParagraphSign,parabegin,paraend,counter_multi_ref,counter_non_identified_ref,counter_non_identified_ref2,CFR_Text,ParagraphList=None):
    Mehrfachverweise = []
    currentposition = parabegin
    T = True
    try:
        currentposition = CFR_Text.index(ParagraphSign, currentposition, paraend)
        if ParagraphSign == "§§" and parabegin == 2137400:
            dummy_tmp = True
            #print("TEST!!!!")
    except:
        T = False
    while T:
        currentposition += len(ParagraphSign)
        nextletter = CFR_Text[currentposition]
        # Relikbehandlung #########
        '''
        if nextletter == " ":# and ParagraphSign == "Sec. Sec. ":
            try:
                currentposition = CFR_Text.index(ParagraphSign, (currentposition + 1), paraend)
                continue
            except:
                break
        '''
        ###########################
        counter_multi_ref += 1
        verweis1 = ""
        spec_sign = 0
        page_break_sign = 0
        while nextletter == " " or nextletter == "\n" or nextletter == "\t":
            currentposition += 1
            nextletter = CFR_Text[currentposition]
        while nextletter != " " and nextletter != ",":
            if nextletter == "\n":
                currentposition += 1
                nextletter = CFR_Text[currentposition]
                continue
            if nextletter == '—':
                break
            if nextletter == "-" and spec_sign == 1:
                break
            elif nextletter == "-" and spec_sign == 0:
                spec_sign = 1
            else:
                spec_sign = 0
            if nextletter == "[" and CFR_Text[(currentposition)] == "[":
                while page_break_sign != 2:
                    currentposition += 1
                    nextletter = CFR_Text[currentposition]
                    if nextletter == "]" and page_break_sign ==0:
                        page_break_sign = 1
                    elif nextletter == "]" and page_break_sign == 1:
                        page_break_sign = 2
                        currentposition += 1
                        continue
            verweis1 += nextletter
            currentposition += 1
            nextletter = CFR_Text[currentposition]

        Case_ = 0
        if CFR_Text[currentposition] == '—':
            Case_  = 6
            currentposition += 1
        elif CFR_Text[currentposition] == "-":
            Case_ = 5  # Notation mit "--"
            currentposition += 1
            verweis1 = verweis1[0:(len(verweis1) - 1)]
        elif CFR_Text[currentposition] == ",":
            Case_ = 3  # Aufzählung
            currentposition += 2

        else:
            # Prüfe, ob es Seitenumbruch gab
            while CFR_Text[currentposition] == "\n":
                currentposition += 1
            if CFR_Text[currentposition] == "[" and CFR_Text[(currentposition + 1)] == "[":
                while CFR_Text[currentposition] != "\n":
                    currentposition += 1
                currentposition += 1
            currentposition += 1
            if CFR_Text[currentposition] == "\n":
                currentposition += 1
            if CFR_Text[currentposition] == "(":
                while CFR_Text[currentposition] != ")":
                    currentposition += 1
                currentposition += 2

            if CFR_Text[currentposition] == "a":
                Case_ = 1  # and
                currentposition += 4
            elif CFR_Text[currentposition] == "t":
                Case_ = 2  # through or to
                currentposition += 1
                if CFR_Text[currentposition] == "o":
                    currentposition += 2
                else:
                    currentposition += 7
                    #print("Hat es erkannt!!!")
            elif CFR_Text[currentposition] == "o":
                Case_ = 4  # or
                currentposition += 3
                
        ### pruefe ob es ein Spezialfall ist ###
        special_case = False        
        if verweis1.find(".")==-1 and (ParagraphSign.find("17 CFR part")!=-1 or ParagraphSign.find("17 CFR Part")!=-1):
            special_case = True
            #help_i = verweis1.find(")")
            help_i = [verweis1.find("("), verweis1.find(")"), verweis1.find("["), verweis1.find("]"),
                  verweis1.find(";"), verweis1.find(","), verweis1.find(":"), verweis1.find("'")]
            index_ = min([help_i[i] if help_i[i] != -1 else (len(verweis1) + 1) for i in range(8)])
            #verweis2 = verweis2[:index_]
            if index_ != (len(verweis1)+1):
                verweis1 = verweis1[:index_]
            # jeden Paragraphen aus dem spezifischen Part hinzufuegen
            if (ParagraphSign.find("17 CFR part ")!=-1 or ParagraphSign.find("17 CFR Part ")!=-1):
                for para_ in ParagraphList:
                    tmp_index = para_.find(".")
                    para_help = para_[0:tmp_index]
                    if verweis1 == para_help:
                        Mehrfachverweise.append(para_)
                #print("Bin hier gelandet", verweis1, "Kontext:", CFR_Text[(currentposition-20):(currentposition+20)])
                try:
                    currentposition = CFR_Text.index(ParagraphSign, (currentposition + 1), paraend)
                except:
                    break
                continue
            #print("Bin hier gelandet", verweis1, "Kontext:", CFR_Text[(currentposition-20):(currentposition+20)])
                
        #!!!!!!!!!!!!
        #if special_case and Case_ == 3:
        #    print(verweis1, "Nächster Buchstabe:", CFR_Text[currentposition], "Kontext:", CFR_Text[(currentposition-5):(currentposition+5)])
        #!!!!!!!!!!!!
        
        verweis2 = ""
        # Prüfe, ob es Seitenumbruch gab
        while CFR_Text[currentposition] == "\n":
           currentposition += 1
           #!!!!!!!!!!!!
           #if special_case and Case_ == 3:
           #    print(verweis1,"Nächster Buchstabe:",CFR_Text[currentposition], "Kontext:", CFR_Text[(currentposition-5):(currentposition+5)])
           #!!!!!!!!!!!!
        if CFR_Text[currentposition] == "[" and CFR_Text[(currentposition + 1)] == "[":
            while CFR_Text[currentposition] != "\n":
                currentposition += 1
            currentposition += 1
        nextletter = CFR_Text[currentposition]
        double_letter = False
        while nextletter != " " and nextletter != ",":
            #!!!!!!!!!!!!
            #if special_case and Case_ == 3:
            #    print(verweis1,"Nächster Buchstabe:",CFR_Text[currentposition], "Kontext:", CFR_Text[(currentposition-5):(currentposition+5)])
            #!!!!!!!!!!!!
            if nextletter != "\n":
                verweis2 += nextletter
            if nextletter.isalpha() and CFR_Text[(currentposition+1)].isalpha():
                double_letter = True
                break
            currentposition += 1
            nextletter = CFR_Text[currentposition]
        verweis2_alt = verweis2
        # print("Verweis2 vor Anpassung ", verweis2, end=", ")
        # Teilweise muss verweis2 korrigiert werden
        # 1) Testen, ob Vorsilbe vorhanden ist oder ob in Abhängigkeit von verweis1
        if special_case == False:
            try:
                if verweis2[0:3].isnumeric() == False or verweis2[3] != ".":
                    verweis2 = verweis1[0:4] + verweis2
            except:
                verweis2 = verweis1[0:4] + verweis2
        if double_letter:
            verweis2 = verweis1
            Case_ = 1
        #print("Verweis2 nach 1) Anpassung ", verweis2, end=", ")
        # 2) Abschneiden von Sonderzeichen am Ende
        help_i = [verweis2.find("("), verweis2.find(")"), verweis2.find("["), verweis2.find("]"),
                  verweis2.find(";"), verweis2.find(","), verweis2.find(":"), verweis2.find("'")]
        index_ = min([help_i[i] if help_i[i] != -1 else (len(verweis2) + 1) for i in range(8)])
        verweis2 = verweis2[:index_]
        if len(verweis2) == 0:
            dummy_ = 1
            print()
            print("Verweis 1:", verweis1, "Verweis 2:", verweis2)
            print(CFR_Text[(currentposition - 30):(currentposition + 30)])
        if verweis2[(len(verweis2) - 1)] == ".":
            verweis2 = verweis2[:(len(verweis2) - 1)]
        # while verweis2[(len(verweis2)-index_)] == "." or verweis2[(len(verweis2)-index_)] == "," or\
        #         verweis2[(len(verweis2)-index_)] == ")" or verweis2[(len(verweis2)-index_)] == ";":
        #     index_ +=1
        # verweis2 = verweis2[0:(len(verweis2)-index_+1)]
        # print("Verweis2 nach Anpassung ", verweis2)
        # AND und OR:
        if Case_ == 1 or Case_ == 4:
            if special_case == False:
                Mehrfachverweise.append(verweis1)
                Mehrfachverweise.append(verweis2)
            else:
                # jeden Paragraphen aus dem spezifischen Part hinzufuegen
                for para_ in ParagraphList:
                    tmp_index = para_.find(".")
                    para_help = para_[0:tmp_index]
                    if verweis1 == para_help:
                      Mehrfachverweise.append(para_)
                    if verweis2 == para_help:
                      Mehrfachverweise.append(para_)  
        # THROUGH
        elif Case_ == 2 or Case_ == 5 or Case_ == 6:
            stop_ = False
            try:
                start_ = 0
                while True:
                    try:
                        tabposition = verweis1.index("\t", start_)
                        nextletter = verweis1[(tabposition + 1)]
                        start_ = tabposition + 1
                        if (nextletter.isnumeric() == False):
                            verweis1 = verweis1[0:tabposition]
                    except:
                        break
                verweis1 = verweis1.replace('\t', '')
                verweis1 = verweis1.replace('O', '0')
                verweis1 = verweis1.replace('I', '1')
                verweis1 = verweis1.replace('l', '1')
                verweis1 = verweis1.replace('!', '1')
                verweis1 = verweis1.replace('Z', '2')
                verweis1 = verweis1.replace('S', '5')
                verweis1 = verweis1.replace('B', '8')
                verweis1 = verweis1.replace('—', '-')
                verweis1 = verweis1.replace(',', '.')
                verweis1 = verweis1.replace('^', '-')
                verweis1 = verweis1.replace('C', 'c')

                verweis1 = verweis1.replace("\n", "")
                index_1 = ParagraphList.index(verweis1)
            except:
                #print("Verweis 1 nicht gefunden", verweis1)
                stop_ = True
            try:
                start_ = 0
                while True:
                    try:
                        tabposition = verweis2.index("\t", start_)
                        nextletter = verweis2[(tabposition + 1)]
                        start_ = tabposition + 1
                        if (nextletter.isnumeric() == False):
                            verweis2 = verweis2[0:tabposition]
                    except:
                        break
                verweis2 = verweis2.replace('\t', '')
                verweis2 = verweis2.replace('O', '0')
                verweis2 = verweis2.replace('I', '1')
                verweis2 = verweis2.replace('l', '1')
                verweis2 = verweis2.replace('!', '1')
                verweis2 = verweis2.replace('Z', '2')
                verweis2 = verweis2.replace('S', '5')
                verweis2 = verweis2.replace('B', '8')
                verweis2 = verweis2.replace('—', '-')
                verweis2 = verweis2.replace(',', '.')
                verweis2 = verweis2.replace('^', '-')
                verweis2 = verweis2.replace('C', 'c')

                verweis2 = verweis2.replace("\n", "")

                index_2 = ParagraphList.index(verweis2)
            except:
                verweis2 = verweis1[0:5] + verweis2[4:]
                try:
                    index_2 = ParagraphList.index(verweis2)
                except:
                    if stop_ == False:
                        #print("Verweis 2 nicht gefunden", verweis2, "(alter Verweis2 :", verweis2_alt,
                        #      ") aber Verweis 1 schon ", verweis1)
                        stop_ = True
            #dummy_ = "help"
            if stop_ == False:
                # print("Through-Verweis geschafft")
                Mehrfachverweise += ParagraphList[index_1:(index_2 + 1)]
                #Dummy_ = "help"
            else:
               # print("Mehrfachverweis nicht geschafft: ", CFR_Text[(currentposition-20):(currentposition+20)])
                counter_non_identified_ref2 += 1

        # Aufzählung
        elif Case_ == 3:
            if special_case == False:
                Mehrfachverweise.append(verweis1)
                Mehrfachverweise.append(verweis2)
            else:
                # jeden Paragraphen aus dem spezifischen Part hinzufuegen
                for para_ in ParagraphList:
                    tmp_index = para_.find(".")
                    para_help = para_[0:tmp_index]
                    if verweis1 == para_help:
                      Mehrfachverweise.append(para_)
                    if verweis2 == para_help:
                      Mehrfachverweise.append(para_)
            #if special_case:
            #        print("Verweis 1:", verweis1, "Verweis 2:", verweis2)
            while nextletter == ",":
                currentposition += 2
                verweis2 = ""
                # Prüfe, ob es Seitenumbruch gab
                while CFR_Text[currentposition] == "\n":
                    currentposition += 1
                if CFR_Text[currentposition] == "[" and CFR_Text[(currentposition + 1)] == "[":
                    while CFR_Text[currentposition] != "\n":
                        currentposition += 1
                    currentposition += 1
                nextletter = CFR_Text[currentposition]
                double_letter = False
                while nextletter != " " and nextletter != ",":
                    if nextletter != "\n":
                        verweis2 += nextletter
                    if nextletter.isalpha() and CFR_Text[(currentposition+1)].isalpha():
                        double_letter = True
                        break
                    currentposition += 1
                    nextletter = CFR_Text[currentposition]
                if double_letter == True:
                    break
                # Teilweise muss verweis2 korrigiert werden
                # 1) Testen, ob Vorsilbe vorhanden ist oder ob in Abhängigkeit von verweis1
                if special_case == False:
                    try:
                        if verweis2[0:3].isnumeric() == False or verweis2[3] != ".":
                            verweis2 = verweis1[0:4] + verweis2
                    except:
                        verweis2 = verweis2[0:(len(verweis2) - index_ + 1)]
                # 2) Abschneiden von Sonderzeichen am Ende
                help_i = [verweis2.find("("), verweis2.find(")"), verweis2.find("["), verweis2.find("]"),
                          verweis2.find(";"), verweis2.find(","), verweis2.find(":"), verweis2.find("'")]
                index_ = min([help_i[i] if help_i[i] != -1 else (len(verweis2) + 1) for i in range(8)])
                verweis2 = verweis2[:index_]
                if len(verweis2) == 0:
                    dummy_ = 1
                    print("Verweis 1:", verweis1, "Verweis 2:", verweis2)
                    print(CFR_Text[(currentposition - 30):(currentposition + 30)])
                    print("Spezialfall erkannt?", special_case)
                    #verweis1.find(".")==-1 and  (ParagraphSign.find("17 CFR part")!=-1 or ParagraphSign.find("17 CFR Part")!=-1)
                    print("ParagraphZeichen:",ParagraphSign)
                    print("Prüfung des Verweis1:",verweis1.find(".")==-1)
                    print("Prüfung des Parazeichens:",ParagraphSign.find("17 CFR part")!=-1 or ParagraphSign.find("17 CFR Part")!=-1)
                    print("Gesamt:",verweis1.find(".")==-1 and  (ParagraphSign.find("17 CFR part")!=-1 or ParagraphSign.find("17 CFR Part")!=-1))
                    
                    
                if verweis2[(len(verweis2) - 1)] == ".":
                    verweis2 = verweis2[:(len(verweis2) - 1)]
                # while verweis2[(len(verweis2)-index_)] == "." or verweis2[(len(verweis2)-index_)] == "," or\
                #         verweis2[(len(verweis2)-index_)] == ")" or verweis2[(len(verweis2)-index_)] == ";":
                #     index_ +=1
                # verweis2 = verweis2[0:(len(verweis2)-index_+1)]
                if special_case == False:
                    Mehrfachverweise.append(verweis2)
                else:
                    # jeden Paragraphen aus dem spezifischen Part hinzufuegen
                    for para_ in ParagraphList:
                        tmp_index = para_.find(".")
                        para_help = para_[0:tmp_index]
                        if verweis2 == para_help:
                            Mehrfachverweise.append(para_)
                #if special_case:
                #   print("Verweis 1:", verweis1, "Verweis 2:", verweis2)
        # Resetfälle:
        elif Case_ == 0:
            # Prüfe, ob es eine Trennung nur mit "-" war:
            try:
                index__ = verweis1.index("-")
                verweis2 = verweis1[(index__+1):len(verweis1)]
                verweis1 = verweis1[0:index__]
                stop_ = False
                try:
                    index_1 = ParagraphList.index(verweis1)
                except:
                    # print("Verweis 1 nicht gefunden", verweis1)
                    stop_ = True
                try:
                    index_2 = ParagraphList.index(verweis2)
                except:
                    verweis2 = verweis1[0:5] + verweis2[4:]
                    try:
                        index_2 = ParagraphList.index(verweis2)
                    except:
                        if stop_ == False:
                            # print("Verweis 2 nicht gefunden", verweis2, "(alter Verweis2 :", verweis2_alt,
                            #      ") aber Verweis 1 schon ", verweis1)
                            stop_ = True
                if stop_ == False:
                    # print("Through-Verweis geschafft")
                    Mehrfachverweise += ParagraphList[index_1:(index_2 + 1)]
                else:
                    counter_non_identified_ref2 += 1
            except:
                counter_non_identified_ref += 1
                #Mehrfachverweise.append(verweis1)
                if special_case == False:
                    counter_non_identified_ref += 1
                    Mehrfachverweise.append(verweis1)
                else:
                    # jeden Paragraphen aus dem spezifischen Part hinzufuegen
                    for para_ in ParagraphList:
                        tmp_index = para_.find(".")
                        para_help = para_[0:tmp_index]
                        if verweis1 == para_help:
                            Mehrfachverweise.append(para_)
                #print("Nicht nachvollzierbarer Mehrfachverweis:", ParagraphSign, verweis1)

        try:
            currentposition = CFR_Text.index(ParagraphSign, (currentposition + 1), paraend)
        except:
            break

    return (Mehrfachverweise,counter_multi_ref,counter_non_identified_ref,counter_non_identified_ref2)