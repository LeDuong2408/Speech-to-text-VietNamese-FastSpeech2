import re
from text import cleaners
from text.symbols import symbols, symbols_vi


# Mappings from symbol to numeric ID and vice versa:
_symbol_to_id = {s: i for i, s in enumerate(symbols)}
_id_to_symbol = {i: s for i, s in enumerate(symbols)}
_symbol_to_id_vi = {s: i for i, s in enumerate(symbols_vi)}
_id_to_symbol_vi = {i: s for i, s in enumerate(symbols_vi)}

# Regular expression matching text enclosed in curly braces:
_curly_re = re.compile(r"(.*?)\{(.+?)\}(.*)")


def text_to_sequence(text, cleaner_names):
    """Converts a string of text to a sequence of IDs corresponding to the symbols in the text.

    The text can optionally have ARPAbet sequences enclosed in curly braces embedded
    in it. For example, "Turn left on {HH AW1 S S T AH0 N} Street."

    Args:
      text: string to convert to a sequence
      cleaner_names: names of the cleaner functions to run the text through

    Returns:
      List of integers corresponding to the symbols in the text
    """
    sequence = []

    is_vietnamese = 'vietnamese_cleaners' in cleaner_names

    # Check for curly braces and treat their contents as ARPAbet:
    while len(text):
        m = _curly_re.match(text)
        if not m:
            sequence += _symbols_to_sequence(_clean_text(text, cleaner_names), is_vietnamese)
            break
        sequence += _symbols_to_sequence(_clean_text(m.group(1), cleaner_names), is_vietnamese)
        sequence += _arpabet_to_sequence(m.group(2), is_vietnamese)
        text = m.group(3)
    return sequence


def sequence_to_text(sequence, vi_lang=False):
    """Converts a sequence of IDs back to a string"""
    result = ""
    id_to_symbol = _id_to_symbol
    if vi_lang:
        id_to_symbol = _id_to_symbol_vi
    for symbol_id in sequence:
        if symbol_id in id_to_symbol:
            s = id_to_symbol[symbol_id]
            # Enclose ARPAbet back in curly braces:
            if len(s) > 1 and s[0] == "@":
                s = "{%s}" % s[1:]
            result += s
    return result.replace("}{", " ")


def _clean_text(text, cleaner_names):
    for name in cleaner_names:
        cleaner = getattr(cleaners, name)
        if not cleaner:
            raise Exception("Unknown cleaner: %s" % name)
        text = cleaner(text)
    return text


def _symbols_to_sequence(symbols, vi_lang=False):
    if vi_lang:
        return [_symbol_to_id_vi[s] for s in symbols if _should_keep_symbol(s, vi_lang)]
    else:
        return [_symbol_to_id[s] for s in symbols if _should_keep_symbol(s, vi_lang)]

def _arpabet_to_sequence(text, vi_lang=False):
    return _symbols_to_sequence(["@" + s for s in text.split()], vi_lang)


def _should_keep_symbol(s, vi_lang=False):
    if vi_lang:
        return s in _symbol_to_id_vi and s != "_" and s != "~"
    else:
        return s in _symbol_to_id and s != "_" and s != "~"


def clean_vietnamese_text(text):
    return cleaners.vietnamese_cleaners(text)