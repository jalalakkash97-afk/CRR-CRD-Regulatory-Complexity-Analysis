''' Version: 23.04.2026
Funktion zur Bestimmung des FRES-Indexes und dafuer benoetigter Komponenten
'''

import nltk
from nltk.tokenize import sent_tokenize
import re
import syllapy
from nltk.corpus import cmudict

def computing_fres(ParagraphList,PositionsParagraph,EndParagraph,CFR_Text):
    # 1.) Rechtschreibpruefung: ... (to be continued)
    
    # 2.) Identifizieren der Saetze pro Paragraph:
    NumParaSent = [0 for index_p in range(len(ParagraphList))]
    for index_p in range(len(ParagraphList)):
        parabegin = PositionsParagraph[index_p]
        paraend = EndParagraph[index_p]
        paratext = CFR_Text[parabegin:paraend]
        parasentence = sent_tokenize(paratext)
        #ParaSentences[index_p] = parasentence
        NumParaSent[index_p] = len(parasentence)
    
    # 3.) Identifizierung der Woerter in den Paragraphen:     
    ParaWords = [[] for index_p in range(len(ParagraphList))]
    NumParaWords = [0 for index_p in range(len(ParagraphList))]
    for index_p in range(len(ParagraphList)):
        parabegin = PositionsParagraph[index_p]
        paraend = EndParagraph[index_p]
        paratext = CFR_Text[parabegin:paraend]
        parawords = re.findall(r'\S+', paratext)
        ParaWords[index_p] = parawords
        NumParaWords[index_p] = len(parawords)
        
    # 4.) Identifizierung der Silben in den Paragraphen:
    d = cmudict.dict()
    def nsyl(word):
        try:
            return [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]][0]
        except KeyError:
            #if word not found in cmudict
            return syllapy.count(word)
            
    NumParaSylla = [0 for index_p in range(len(ParagraphList))]
    for index_p in range(len(ParagraphList)):
        for index_w in range(len(ParaWords[index_p])):
            NumParaSylla[index_p] += nsyl((ParaWords[index_p])[index_w])
            
    # 5.) Berechnung des FRES:
    FRESPara = [0 for index_p in range(len(ParagraphList))]
    for index_p in range(len(ParagraphList)):
        FRESPara[index_p] = 206.835 - 1.015*(NumParaWords[index_p]/NumParaSent[index_p]) - 84.6*(NumParaSylla[index_p]/NumParaWords[index_p])
    
    return (FRESPara, NumParaSent, NumParaWords, NumParaSylla)