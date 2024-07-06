from enum import Enum
from .data.i18n.ar_en import translations as ar_en_translations
from .data.i18n.ar import translations as ar_translations
from .data.i18n.en import translations as en_translations
class Lang(Enum):
    AR_EN = "ar_en"
    AR = "ar"
    EN = "en"

class i18n:
    def __init__(self, lang: Lang = Lang.AR_EN):
        self.lang = lang

    def t(self, key: str, default: str = None) -> str:
        if self.lang in data:
            if key in data[self.lang]:
                return data[self.lang][key]
        if Lang.AR_EN in data:
            if key in data[Lang.AR_EN]:
                return data[Lang.AR_EN][key]
        return default
    
data = {
    Lang.AR_EN: ar_en_translations,
    Lang.AR: ar_translations,
    Lang.EN: en_translations,
}
