'''Version: 27.04.2026
Funktionen, die die (Gewichts-) Faktoren eines Zirkels/Schleife bzw. eines Verweises aus einem Zirkel bestimmen

'''

# Faktor für die Verweise aus einem Zirkels heraus
def verweis_factor_fun(exp_ref_factor, len_zirkel):
        if exp_ref_factor == 1:
            if len_zirkel == 1:
                return 1
            else:
                # return (len_zirkel + 1) / len_zirkel # (bis 9.11.2024)
                # return (len_zirkel + 1) / (2*len_zirkel) # (ab 9.11.2024)
                return 1  # (ab 12.03.2025)
        else:
            #print("??? Wie?")
            # return (exp_ref_factor*(exp_ref_factor ** (len_zirkel+1)-1) / (exp_ref_factor - 1)) / len_zirkel # (bis 9.11.2024)
            # return exp_ref_factor*(1/(len_zirkel**2)/(exp_ref_factor-1)*(-len_zirkel+exp_ref_factor*(exp_ref_factor**len_zirkel-1)/(exp_ref_factor-1)))    # (ab 9.11.2024)
            return exp_ref_factor * (1 / len_zirkel) * ((exp_ref_factor ** len_zirkel - 1) / (exp_ref_factor - 1))  # (ab 12.03.2025)
            #return exp_ref_factor # (ab 11.03.2026)


# Faktor für Gesamtkosten des Zirkels
def zirkel_factor_fun(exp_ref_factor, len_zirkel):
        if exp_ref_factor == 1:
            if len_zirkel == 1:
                return 1
            else:
                # return (len_zirkel + 1) / len_zirkel # (bis 9.11.2024)
                # return (len_zirkel + 1) / (2*len_zirkel)  # (ab 9.11.2024)
                return 1  # (ab 12.03.2025)
        else:
            #print("??? Wie?")
            # return (exp_ref_factor ** (len_zirkel+1)-1) / (exp_ref_factor - 1) / len_zirkel # (bis 9.11.2024)
            # return 1/(len_zirkel**2)/(exp_ref_factor - 1)*(-len_zirkel + exp_ref_factor*(exp_ref_factor**len_zirkel - 1)/(exp_ref_factor - 1))  # (ab 9.11.2024)
            return (1 / len_zirkel) * ((exp_ref_factor ** len_zirkel - 1) / (exp_ref_factor - 1))  # (ab 12.03.2025)