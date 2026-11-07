from collections import defaultdict
from translate import Translator


qwestions = {
    'как тебя зовут': 'Я супер-крутой-бот и мое предназначение — помогать тебе!',
    'сколько тебе лет': 'Это слишком философский вопрос',
    'привет': 'Привет! Чем могу помочь?',
}


class TextAnalysis:
    memory = defaultdict(list)

    def __init__(self, text, owner, from_lang="ru", to_lang="en"):
        owner_key = owner or "unknown"
        TextAnalysis.memory[owner_key].append(self)

        self.text = text or ""
        self.from_lang = from_lang.lower()
        self.to_lang = to_lang.lower()
        self.translation = self.__translate(self.text, self.from_lang, self.to_lang)

        if self.text.lower() in qwestions.keys():
            self.response = qwestions[self.text.lower()]
        else:
            self.response = self.get_answer()

    def __build_response(self, text):
        if not text:
            return "Пустое сообщение."
        return f"Я получил твое сообщение: {text}"

    def get_answer(self):
        return self.__build_response(self.text)

    def __translate(self, text, from_lang, to_lang):
        if not text:
            return ""
        if from_lang == to_lang:
            return text

        try:
            translator = Translator(from_lang=from_lang, to_lang=to_lang)
            return translator.translate(text)
        except Exception:
            return "Перевод не удался"
