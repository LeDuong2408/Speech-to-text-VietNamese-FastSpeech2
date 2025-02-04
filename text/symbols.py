""" from https://github.com/keithito/tacotron """

"""
Defines the set of symbols used in text input to the model.

The default is a set of ASCII characters that works well for English or text that has been run through Unidecode. For other data, you can modify _characters. See TRAINING_DATA.md for details. """

from text import cmudict, vietnamese_phonemes

_pad = "_"
_punctuation = "!'(),.:;? "
_special = "-"
_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" # English
_letters_vi  = 'aáảàãạâấẩầẫậăắẳằẵặbcdđeéẻèẽẹêếểềễệfghiíỉìĩịjklmnoóỏòõọôốổồỗộơớởờỡợpqrstuúủùũụưứửừữựvwxyýỷỳỹỵz' # Tiếng Việt 

_silences = ["@sp", "@spn", "@sil"]

# Prepend "@" to ARPAbet symbols to ensure uniqueness (some are the same as uppercase letters):
_arpabet = ["@" + s for s in cmudict.valid_symbols]
_vietnamese_phonemes = ["@" + s for s in vietnamese_phonemes.valid_symbols]

# Export all symbols English
symbols = (
    [_pad]
    + list(_special)
    + list(_punctuation)
    + list(_letters)
    + _arpabet
    + _silences
)

# Export all symbols Vietnamese
symbols_vi = (
    [_pad]
    + list(_special)
    + list(_punctuation)
    + list(_letters_vi)
    + _vietnamese_phonemes
    + _silences
)

def get_symbols(vi_lang=False):
    if vi_lang:
        return symbols_vi
    else:
        return symbols
