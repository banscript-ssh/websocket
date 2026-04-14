# ============================== # LOGIC GATE CASE # ==============================
def run_logic_case(case_name: str, a: bool, b: bool):
    if case_name == "AND":
        result = a and b
    elif case_name == "OR":
        result = a or b
    elif case_name == "XOR":
        result = a ^ b
    elif case_name == "NAND":
        result = not (a and b)
    elif case_name == "NOR":
        result = not (a or b)
    else:
        result = False

    return {
        "LED1": int(a),
        "LED2": int(b),
        "LED3": int(result)
    }