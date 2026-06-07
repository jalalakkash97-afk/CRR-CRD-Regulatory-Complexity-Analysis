''' Version: 22.04.2026
Funktion zur Bestimmung zur Bestimmung des Index eines Paragraphen-Verweises in dem Array der Paragraphen des Textes
'''
def index_verweise(verweis, ParagraphList):

    try:
        index1 = ParagraphList.index(verweis)
        return index1
    except:
        return len(ParagraphList)