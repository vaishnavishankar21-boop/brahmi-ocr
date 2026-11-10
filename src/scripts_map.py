import unicodedata

CONS = {
    "k": "KA", "kh": "KHA", "g": "GA", "gh": "GHA",
    "ch": "CA", "chh": "CHA", "j": "JA", "jh": "JHA",
    "t": "TA", "th": "THA", "d": "DA", "dh": "DHA", "n": "NA",
    "p": "PA", "ph": "PHA", "b": "BA", "bh": "BHA", "m": "MA",
    "y": "YA", "r": "RA", "l": "LA", "v": "VA", "w": "VA",
    "s": "SA", "sh": "SHA", "h": "HA",
    "f": "PHA", "z": "JA", "q": "KA", "c": "KA",
}
CONS_KEYS = sorted(CONS, key=len, reverse=True)
VOWEL_KEYS = ["aa", "ai", "au", "ee", "ii", "oo", "uu", "a", "e", "i", "o", "u"]
ALIAS = {"ee": "ii", "oo": "uu"}

# Tamil has no separate letters for these sounds, so they share a letter.
TAMIL_MERGE = {
    "KHA": "KA", "GA": "KA", "GHA": "KA",
    "CHA": "CA", "JHA": "JA",
    "TTHA": "TTA", "DDA": "TTA", "DDHA": "TTA",
    "THA": "TA", "DA": "TA", "DHA": "TA",
    "PHA": "PA", "BA": "PA", "BHA": "PA",
}


def _lookup(text):
    try:
        return unicodedata.lookup(text)
    except KeyError:
        return None


def letter_in(script, name, eo="long"):
    if script == "TAMIL":
        name = TAMIL_MERGE.get(name, name)
    if script in ("KANNADA", "TAMIL") and eo == "long":
        name = {"E": "EE", "O": "OO"}.get(name, name)
    return _lookup(f"{script} LETTER {name}")


def sign_in(script, v, eo="long"):
    if script in ("KANNADA", "TAMIL") and eo == "long":
        v = {"E": "EE", "O": "OO"}.get(v, v)
    return _lookup(f"{script} VOWEL SIGN {v}")


def virama_in(script):
    return _lookup(f"{script} SIGN VIRAMA") or ""


def take(word, i, keys):
    for k in keys:
        if word.startswith(k, i):
            return k
    return None


def parse_word(word, final_virama=True):
    tokens = []
    after = False
    i = 0
    while i < len(word):
        orig = take(word, i, VOWEL_KEYS)
        if orig:
            i += len(orig)
            v = ALIAS.get(orig, orig)
            if after:
                if v != "a":
                    tokens.append(("sign", v.upper()))
                after = False
            else:
                tokens.append(("vowel", v.upper()))
            continue
        c = take(word, i, CONS_KEYS)
        if c:
            i += len(c)
            if after:
                tokens.append(("virama", ""))
            tokens.append(("cons", CONS[c]))
            after = True
            continue
        if after and final_virama:
            tokens.append(("virama", ""))
        after = False
        tokens.append(("other", word[i]))
        i += 1
    if after and final_virama:
        tokens.append(("virama", ""))
    return tokens


def render(tokens, script, eo="long"):
    out = []
    for kind, val in tokens:
        if kind in ("vowel", "cons"):
            out.append(letter_in(script, val, eo) or "?")
        elif kind == "sign":
            out.append(sign_in(script, val, eo) or "?")
        elif kind == "virama":
            out.append(virama_in(script))
        else:
            out.append(val)
    return "".join(out)