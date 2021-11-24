

def convertToBinary(text):
    binary_converted ="  ".join(f"{ord(i):08b}" for i in text)
    return binary_converted

def convertToString(binarieText):


    binary_values = binarieText.split()
    ascii_string = ""
    for binary_value in binary_values:
        an_integer = int(binary_value, 2)
        ascii_character = chr(an_integer)
        ascii_string += ascii_character
        # print(binary_value)
    # print(ascii_string)
    return ascii_string