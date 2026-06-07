'''Version: 23.04.2026
Funktion zum Laden des regulatorischen Textes

'''
def load_text(file_name):
    fobj = open(file_name, "r", encoding="utf-8", errors="ignore")
    i = 0
    CFR_Text = ""
    for line in fobj:
        CFR_Text += str(line)
        i = i + 1

    fobj.close()
    
    return (CFR_Text)