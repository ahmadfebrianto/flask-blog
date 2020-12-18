from googletrans import Translator
from time import sleep

def detect_language(text):
    translator = Translator()
    lang = None
    while lang == None:
        try:
            lang = translator.detect(text)
        except:
            translator = Translator()
            sleep(0.5)
            pass
    return lang


def translate_language(text, dest='en'):
    translator = Translator()
    result = None
    while result == None:
        try:
            result = translator.translate(text, dest=dest)
        except:
            translator = Translator()
            sleep(0.5)
            pass
    return result
