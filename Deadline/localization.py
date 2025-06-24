import gettext
import locale

_podir = "po"
translation = gettext.translation("Deadline", _podir, fallback=True)

LOCALES = {
    ("ru_RU", "UTF-8"): gettext.translation("Deadline", _podir, ["ru_RU.UTF-8"]),
    ("en_US", "UTF-8"): gettext.NullTranslations(),
}


def _(text):
    return LOCALES[locale.getlocale()].gettext(text)
