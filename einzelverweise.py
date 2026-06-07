'''Version: 22.04.2026
Funktion zur Identifizierung und Auswertung von Einzelverweisen

'''

import numpy as np
from functools import cmp_to_key
import copy

def einzelverweise(ParagraphSign,parabegin,paraend, CFR_Text):
    Einzelverweise = []
    currentposition = parabegin
    T = True
    try:
        currentposition = CFR_Text.index(ParagraphSign, currentposition, paraend)
    except:
        T = False
    while T:
        # PositionsParagraph.append(currentposition)
        verweis = ""
        currentposition += (len(ParagraphSign)-1)
        nextletter = CFR_Text[currentposition]
        while nextletter != " " and nextletter != "[":
            verweis += nextletter
            currentposition += 1
            nextletter = CFR_Text[currentposition]
        Einzelverweise.append(verweis)
        try:
            currentposition = CFR_Text.index(ParagraphSign, (currentposition + 1), paraend)
        except:
            break
    return Einzelverweise