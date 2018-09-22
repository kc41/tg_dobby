import re

from transliterate import translit


def escape_test_suffix(txt):
    return re.sub(r"[\s\-]+", "_", translit(txt.lower(), reversed=True, language_code="ru"))
