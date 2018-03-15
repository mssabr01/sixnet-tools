def int_to_hex_string(int):
    """Converts an integer to a 2 digit hex string without the 0x prefix"""
    if(int < 16):
        return hex(int).replace("x","")
    else:
        return hex(int).replace("0x","")