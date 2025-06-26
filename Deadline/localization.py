import gettext
import locale
import os

_podir = os.path.join(os.path.dirname(__file__), "po")
translation = gettext.translation("Deadline", _podir, fallback=True)

LOCALES = {
    ("ru_RU", "UTF-8"): gettext.translation("Deadline", _podir, ["ru_RU.UTF-8"]),
    ("en_US", "UTF-8"): gettext.NullTranslations(),
}


def _(text):
    return LOCALES[locale.getlocale()].gettext(text)
