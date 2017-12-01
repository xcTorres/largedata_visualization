import redis
import time
import mercantile
def quadkey_to_num(qk):
    number = 0
    for i, digit in enumerate(qk):
        number  |= int(digit)
        if i != len(qk)-1:
            number = number << 2

    return str(len(qk))+"_"+ str(number)

print quadkey_to_num('0')