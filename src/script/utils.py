import os
import base64


BOUNCEABLE_TAG = b'\x11'
NONBOUNCEABLE_TAG = b'\x51'


def calcCRC(message):
    poly = 0x1021
    reg = 0
    message += b'\x00\x00'
    for byte in message:
        mask = 0x80
        while(mask > 0):
            reg <<= 1
            if byte & mask:
                reg += 1
            mask >>= 1
            if reg > 0xffff:
                reg &= 0xffff
                reg ^= poly
    return reg.to_bytes(2, "big")


def addr_from_file(file_name):
    if not os.path.exists(file_name):
        return None

    with open(file_name, 'rb') as f:
        bytes = f.read()
        addr_bytes, wc_bytes = bytes[:32], bytes[32:]
        wc = int.from_bytes(wc_bytes, byteorder='big', signed=True)
        wc_bytes = b'\xff' if wc == -1 else wc.to_bytes(1, "big")

    preaddr_b = BOUNCEABLE_TAG + wc_bytes + addr_bytes
    preaddr_u = NONBOUNCEABLE_TAG + wc_bytes + addr_bytes
    b64_b = base64.urlsafe_b64encode(preaddr_b + calcCRC(preaddr_b)).decode('utf8')
    b64_u = base64.urlsafe_b64encode(preaddr_u + calcCRC(preaddr_u)).decode('utf8')

    return { 'b': b64_b, 'u': b64_u }
