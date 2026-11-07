import unicodedata

DEVANAGARI = {
    "A": "अ", "AA": "आ", "I": "इ", "II": "ई", "U": "उ", "UU": "ऊ",
    "VOCALIC R": "ऋ", "VOCALIC RR": "ॠ", "VOCALIC L": "ऌ", "VOCALIC LL": "ॡ",
    "E": "ए", "AI": "ऐ", "O": "ओ", "AU": "औ",
    "KA": "क", "KHA": "ख", "GA": "ग", "GHA": "घ", "NGA": "ङ",
    "CA": "च", "CHA": "छ", "JA": "ज", "JHA": "झ", "NYA": "ञ",
    "TTA": "ट", "TTHA": "ठ", "DDA": "ड", "DDHA": "ढ", "NNA": "ण",
    "TA": "त", "THA": "थ", "DA": "द", "DHA": "ध", "NA": "न",
    "PA": "प", "PHA": "फ", "BA": "ब", "BHA": "भ", "MA": "म",
    "YA": "य", "RA": "र", "LA": "ल", "LLA": "ळ", "VA": "व",
    "SHA": "श", "SSA": "ष", "SA": "स", "HA": "ह",
}

def letter_name(code_hex):
    return unicodedata.name(chr(int(code_hex, 16)), "?").replace("BRAHMI LETTER ", "")

def to_latin(name):
    return name.replace("VOCALIC ", "").lower()

def to_devanagari(name):
    return DEVANAGARI.get(name, "?")

if __name__ == "__main__":
    missing = 0
    for code in range(0x11005, 0x11035):
        name = letter_name(f"{code:X}")
        dev = to_devanagari(name)
        if dev == "?":
            missing += 1
        print(f"{code:X}  {name:12} {to_latin(name):6} {dev}")
    print("missing:", missing)