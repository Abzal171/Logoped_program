import os
import json
import pyaudio
from vosk import Model, KaldiRecognizer
import pyttsx3
import sys
from PyQt5 import QtWidgets

def similar(a, b):
    return sum([1 for char_a, char_b in zip(a, b) if char_a == char_b]) / max(len(a), len(b))

def load_config():
    config_file = "config.json"
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
        return config
    else:
        return {"similarity_threshold": 0.7, "max_attempts": 5}

def handle_error(language_choice, speech_defect_choice, base_dir):
    LANG_HELP_DIR = os.path.join(base_dir, 'lang_help')
    help_files = {
        "1": {
            "1": os.path.join(LANG_HELP_DIR, 'kz_rotacizm_help.txt'),
            "2": os.path.join(LANG_HELP_DIR, 'kz_sigmatizm_help.txt'),
            "3": os.path.join(LANG_HELP_DIR, 'kz_lambdacia_help.txt')
        },
        "2": {
            "1": os.path.join(LANG_HELP_DIR, 'ru_rotacizm_help.txt'),
            "2": os.path.join(LANG_HELP_DIR, 'ru_sigmatizm_help.txt'),
            "3": os.path.join(LANG_HELP_DIR, 'ru_lambdacia_help.txt')
        }
    }

    help_file = help_files.get(language_choice, {}).get(speech_defect_choice)
    if help_file:
        try:
            os.startfile(help_file)
        except FileNotFoundError:
            print("Файл с рекомендациями не найден.")
    else:
        print("Некорректный выбор. Завершение программы.")

def save_recognition_result_to_file(language, defect, recognized_text):
    try:
        with open('Save_words.txt', 'a', encoding='utf-8') as file:
            file.write(f"Тіл/Язык: {language}, Мүкістік/Дефект: {defect}, Сөз/Слово: {recognized_text}\n")
            if language == "1":
                print("Мәліметтер файлға сәтті сақталды")
            elif language == "2":
                print("Данные успешно сохранены в файл.")
    except Exception as e:
        if language == "1":
            print(f"Файлге мәліметтерді сақтау кезінде қате пайда болды: {e}")
        elif language == "2":
            print(f"Ошибка при записи данных в файл: {e}")

def speak_words(words):
    engine = pyttsx3.init()
    for word in words:
        engine.say(word)
        engine.runAndWait()

def return_to_main_menu(language_choice, parent_window):
        parent_window.close()
        from MainWin import Ui_MainWindow
        main_window = QtWidgets.QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(main_window)
        main_window.show()

def return_to_language_selection(parent_window):
    parent_window.close()
    from language_selection_window import Ui_MainWindow
    lang_selection_window = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(lang_selection_window)
    lang_selection_window.show()

def main(language_choice, speech_defect_choice, parent_window=None):
    global recognizer, stream, mic, running
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_dir = os.path.join(base_dir, 'lang_model')
        model_path = os.path.join(model_dir, 'kz_big') if language_choice == "1" else os.path.join(model_dir, 'ru_small')
        print("Қазақ тілі режимі таңдалды." if language_choice == "1" else "Выбран режим для русского языка.")

        model = Model(model_path)
        recognizer = KaldiRecognizer(model, 16000)
        mic = pyaudio.PyAudio()
        stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
        stream.start_stream()

        config = load_config()
        running = True

        while running:
            etalon_words = get_etalon_words(language_choice, speech_defect_choice)
            print("Режим выбран, произнесите слова:" if language_choice == "1" else "Выбран режим, произнесите слова:")
            print("Осы сөздерді айтып көріңіз" if language_choice == "1" else "Попробуйте произнести эти слова:", ', '.join(etalon_words))
            speak_words(etalon_words)

            similarity_threshold = config["similarity_threshold"]
            max_attempts = config["max_attempts"]
            attempts = 0
            correct_count = 0

            while attempts < max_attempts and running:
                data = stream.read(4096)
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    recognized_text = result["text"]
                    user_words = recognized_text.split()

                    for word in user_words:
                        word = word.strip('"')
                        max_similarity = max([similar(word, etalon_word) for etalon_word in etalon_words])
                        if max_similarity >= similarity_threshold:
                            correct_count += 1
                            print(f"Сөз '{word}' сәтті анықталды!" if language_choice == "1" else f"Слово '{word}' успешно распознано!")
                            save_recognition_result_to_file(language_choice, speech_defect_choice, word)  # Сохранение слова в файл
                        else:
                            print(f"Сөз, салыстырылған сөздермен сәйкес келмейді: '{word}'" if language_choice == "1" else f"Слово, не похожее на сравниваемые: '{word}'")
                            save_recognition_result_to_file(language_choice, speech_defect_choice, word)

                    if correct_count == len(etalon_words):
                        print("Поздравляем, вы успешно произнесли все слова! Вы справились! " if language_choice == "2" else "Құттықтаймыз!Сіз барлық сөздерді дұрыс айттыңыз!Жарайсыз!")
                        print("Желаете что-то еще?" if language_choice == "2" else "Тағы бірдеңке қалайсызба?")
                        print(
                            "4. Вернуться на главное меню" if language_choice == "2" else "4.Басты мәзірге қайта оралу")
                        print("5. Выйти из программы" if language_choice == "2" else "5.Бағдарламадан шығу")
                        if parent_window:
                            parent_window.command_input.setEnabled(True)
                            parent_window.send_button.setEnabled(True)
                        return

                    attempts += 1
                    if attempts == max_attempts:
                        print("Вы не смогли произнести правильно все слова. Попробуйте:" if language_choice == "2" else "Сіз көрсетілген сөздерді айта алмадыңыз.Келесіден таңдаңыз:")
                        print("1. Попробовать снова" if language_choice == "2" else "1. Қайтадан айтып көру")
                        print("2. Получить рекомендацию" if language_choice == "2" else "2. Анықтама алу")
                        print("3. Тілді қайтадан таңдау/Вернуться к выбору языка")
                        if parent_window:
                            parent_window.command_input.setEnabled(True)
                            parent_window.send_button.setEnabled(True)
                        return  # Завершение программы после открытия рекомендаций

    except Exception as e:
        print(f"Произошла ошибка: {e}")

def process_command(command, language_choice, speech_defect_choice, parent_window):
    global running
    if command == "1":
        main(language_choice, speech_defect_choice, parent_window)
    elif command == "2":
        handle_error(language_choice, speech_defect_choice, os.path.dirname(os.path.abspath(__file__)))
    elif command == "3":
        running = False
        return_to_language_selection(parent_window)
    elif command == "4":
        running = False
        return_to_main_menu(language_choice, parent_window)
    elif command == "5":
        running = False
        sys.exit()

def get_etalon_words(language_choice, speech_defect_choice):
    if language_choice == "1":
        if speech_defect_choice == "1":
            return ['Раушан', 'Картоп', 'Арпа']
        elif speech_defect_choice == "2":
            return ['Шипа', 'Шалқар', 'Жарқын']
        elif speech_defect_choice == "3":
            return ['Бала', 'Алмұрт', 'Шалбар']
    elif language_choice == "2":
        if speech_defect_choice == "1":
            return ['Трактор', 'Раритет', 'Рулет']
        elif speech_defect_choice == "2":
            return ['Саша', 'Шоссе', 'Шершавый']
        elif speech_defect_choice == "3":
            return ['Мелочь', 'Лист', 'Капля']
    return []

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <language_choice> <speech_defект_choice>")
        sys.exit(1)
    language_choice = sys.argv[1]
    speech_defect_choice = sys.argv[2]
    main(language_choice, speech_defect_choice)
