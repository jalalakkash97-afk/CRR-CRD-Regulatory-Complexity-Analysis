''' Version: 22.04.2026
Funktion zur Bestimmung der Paragraphenanfänge und -enden

'''

import numpy as np
from functools import cmp_to_key
import copy

def paragraphenbeginend(ParagraphSign,EndSigns, CFR_Text):
    anfang = []
    enden = []
    currentposition = 0
    start_ = True
    try:
        currentposition = CFR_Text.index(ParagraphSign, currentposition)
        currentposition = currentposition + len(ParagraphSign) -1
    except:
        start_ = False
    while start_:
        anfang.append(currentposition)
        endpos = [CFR_Text.find(EndSigns[i], (currentposition + 1)) for i in range(len(EndSigns))]
        #endpos = [CFR_Text.find(EndSign1, (currentposition + 1)), CFR_Text.find(EndSign2, (currentposition + 1)),
        #          CFR_Text.find(EndSign3, (currentposition + 1)), CFR_Text.find(EndSign4, (currentposition + 1)),
        #          CFR_Text.find(EndSign5, (currentposition + 1))]
        #if currentposition == 1260321:
        #    dummy = 1
        endpos = [endpos[i] if endpos[i] != -1 else (len(CFR_Text) - 1) for i in range(len(endpos))]
        try:
            endpos.append(CFR_Text.index(ParagraphSign, (currentposition + 1)))
        except:
            pass        
        endpos = min(endpos)
        enden.append(endpos)
        try:
            currentposition = CFR_Text.index(ParagraphSign, (currentposition + 1))
            currentposition = currentposition + len(ParagraphSign) - 1
        except:
            break
    return (anfang,enden)