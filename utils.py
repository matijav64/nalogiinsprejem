import unicodedata
from datetime import datetime

def unify_string(s):
    if not s:
        return ""
    return unicodedata.normalize('NFC', s).replace("\u00A0", " ")

def parse_datum(val):
    """Reads a date in ddmmYYYY or dd.mm.YYYY format and returns a tuple (YYYY-mm-dd, ddmmYYYY)."""
    val = unify_string(val.strip())
    if len(val) == 8 and val.isdigit():
        dd, mm, yyyy = val[:2], val[2:4], val[4:]
        dt = datetime.strptime(f"{dd}.{mm}.{yyyy}", "%d.%m.%Y")
    else:
        dt = datetime.strptime(val, "%d.%m.%Y")
    return dt.strftime("%Y-%m-%d"), dt.strftime("%d%m%Y")

def format_ymd_to_ddmmYYYY(ymd):
    if not ymd:
        return ""
    try:
        dt = datetime.strptime(ymd, "%Y-%m-%d")
        return dt.strftime("%d%m%Y")
    except Exception:
        return ymd

def normalize_text(text):
    """
    Normalize text by:
      1. Unifying Unicode (NFC)
      2. Decomposing (NFKD) and stripping diacritics using unidecode if available.
      3. Converting to lowercase.
    """
    if not text:
        return ""
    try:
        import unidecode
        return unidecode.unidecode(text).casefold()
    except ImportError:
        # Fallback: remove diacritics manually (this may be less robust)
        text = unify_string(text)
        decomposed = unicodedata.normalize('NFKD', text)
        ascii_text = decomposed.encode('ASCII', 'ignore').decode('ASCII')
        return ascii_text.casefold()
