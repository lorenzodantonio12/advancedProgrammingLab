def get_range(operator: str, value: float):

    if operator == '=':  
        return (value, value, True, True)
    if operator == '>':  
        return (value, float('inf'), False, False)
    if operator == '>=': 
        return (value, float('inf'), True, False)
    if operator == '<':  
        return (float('-inf'), value, False, False)
    if operator == '<=': 
        return (float('-inf'), value, False, True)
    
    return (0, 0, False, False) 

def check_overlap(op1: str, val1: float, op2: str, val2: float) -> bool:
    
    min1, max1, inc_min1, inc_max1 = get_range(op1, val1)
    min2, max2, inc_min2, inc_max2 = get_range(op2, val2)

    if max1 < min2 or max2 < min1:
        return False

    if max1 == min2:
        return inc_max1 and inc_min2
    if max2 == min1:
        return inc_max2 and inc_min1

    # 3. In tutti gli altri casi, gli intervalli si accavallano!
    return True