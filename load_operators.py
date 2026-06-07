'''Version: 23.04.2026
Funktion zum laden der Operatoren (regulatorische, logische, mathematische)
'''

def load_operators():
    file_name_dic = r"C:\Users\jalal\OneDrive\Desktop\Code_Bearbeitet\operator_dic.csv"
    fobj_dic = open(file_name_dic, "r")#, encoding='UTF-8')
    reg_operators = []
    log_operators = []
    math_operators = []

    for line in fobj_dic:
        line_splited = line.split(",")
        operator_type = (str(line_splited[2]).replace('"','')).replace('\n','')
        operator = (str(line_splited[1]).replace('"','')).replace('\n','')
        if (operator_type == 'LogicalConnectors'):
            log_operators.append(operator)
        elif (operator_type == 'MathematicalOperators'):
            math_operators.append(operator)
        elif (operator_type == 'RegulatoryOperators'):
            reg_operators.append(operator)
        else:
            print(line)
    #print(len(log_operators))
    #print(math_operators)
    #print(len(reg_operators))
    fobj_dic.close()
    
    return (reg_operators,log_operators,math_operators)