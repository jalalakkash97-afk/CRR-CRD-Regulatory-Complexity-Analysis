'''Version: 23.04.2026
Funktion zum Zaehlen der Operatoren je Paragraph
'''

def operator_counting(dictionary_,ParagraphList,PositionsParagraph,EndParagraph,CFR_Text):
    Operators_per_Paragraph = []
    for i in range(len(ParagraphList)):
        # if i%100 ==0:
        #    print(i)
        counter = 0
        parabegin = PositionsParagraph[i]
        paraend = EndParagraph[i]
        for operator_ in dictionary_:
            # print(operator_)
            currentposition = parabegin
            while True:
                try:
                    currentposition = CFR_Text.index(operator_, (currentposition + 1), paraend)
                    counter += 1
                except:
                    break
        Operators_per_Paragraph.append(counter)
        
    return Operators_per_Paragraph