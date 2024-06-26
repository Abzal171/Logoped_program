import os
import json
import pyaudio
from vosk import Model, KaldiRecognizer
import pyttsx3

# Функция для определения степени схожести двух строк
def similar(a, b):
    return sum([1 for char_a, char_b in zip(a, b) if char_a == char_b]) / max(len(a), len(b))

# Загрузка конфигурации из файла
def load_config():
    config_file = "config.json"
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
        return config
    else:
        # Создаем стандартную конфигурацию, если файл не найден
        return {"similarity_threshold": 0.7, "max_attempts": 5}

# Обработка ошибки и вывод рекомендаций пользователю через текстовый файл
def handle_error(language_choice, speech_defect_choice):
    LANG_HELP_DIR = r'C:\Users\Public\Downloads\Diplon\lang_help'
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

# Сохранение результатов распознавания в файл
def save_recognition_result_to_file(language, defect, recognized_text):
    try:
        with open('Save_words.txt', 'a', encoding='utf-8') as file:
            file.write(f"Language: {language}, Defect: {defect}, Recognized Text: {recognized_text}\n")
            if language == "1":
                print("Мәліметтер файлға сәтті сақталды")
            elif language == "2":
                print("Данные успешно сохранены в файл.")
    except Exception as e:
        if language == "1":
            print(f"Файлге мәліметтерді сақтау кезінде қате пайда болды: {e}")
        elif language == "2":
            print(f"Ошибка при записи данных в файл: {e}")

# Функция для произнесения слов
def speak_words(words):
    engine = pyttsx3.init()
    for word in words:
        engine.say(word)
        engine.runAndWait()

# Функция для возвращения в главное меню или выхода из программы
def return_to_main_menu(language_choice):
    while True:
        print("Желаете что-то еще?" if language_choice == "2" else "Тағы бірдеңке қалайсызба?")
        print("1. Вернуться на главное меню" if language_choice == "2" else "1.Басты мәзірге қайта оралу")
        print("2. Выйти из программы" if language_choice == "2" else "2.Бағдарламадан шығу")
        choice = input().strip()
        if choice == "1":
            return True
        elif choice == "2":
            print("Завершение программы." if language_choice == "1" else "Бағдарлама аяқталды.")
            return False
        else:
            print("Некорректный выбор. Повторите попытку.")

# Основная функция программы
def main():
    try:
        while True:
            print("Программа 'Логопед'.")
            print("Для запуска программы нажмите Enter.")
            input()

            print("Тіл/Язык")
            print("1. Қазақ тілі")
            print("2. Русский")
            print("3. Бағдарламадан шығу/Выйти из программы")
            language_choice = input().strip()

            if language_choice == "3":
                print("Бағдарлама аяқталды/Завершение программы.")
                break

            if language_choice not in ["1", "2"]:
                print("Некорректный выбор. Повторите попытку.")
                continue

            model_path = r'C:\Users\Public\Downloads\Diplon\lang_model\kz_big' if language_choice == "1" else r'C:\Users\Public\Downloads\Diplon\lang_model\ru_small'
            print("Қазақ тілі режимі таңдалды." if language_choice == "1" else "Выбран режим для русского языка.")

            model = Model(model_path)
            recognizer = KaldiRecognizer(model, 16000)
            mic = pyaudio.PyAudio()
            stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
            stream.start_stream()

            config = load_config()

            try:
                print("Начинается распознавание. Для остановки скажите 'стоп'." if language_choice == "2" else "Тану басталды. Тоқтату үшін 'стоп' деп айтыңыз.")
                try_again = True  # Флаг для управления повторными попытками

                while try_again:
                    print("Сізде тіл мүкістігінің қандай түрі?" if language_choice == "1" else "Какой дефект речи у вас?")
                    print("1. Ротацизм (картавость)" if language_choice == "2" else "1.Ротацизм(Р әрпін айта алмау)")
                    print("2. Сигматизм (шепелявость)" if language_choice == "2" else "2.Сигмацизм(Ш немесе Ж әрпін айта алмау)")
                    print("3. Ламбдация (проблема с произношением буквы 'л')" if language_choice == "2" else "3.Ламбдация(Л әрпін айта алмау)")
                    print("4. Вернуться к выбору языка" if language_choice == "2" else "4.Тілді қайта таңдау")
                    speech_defect_choice = input().strip()

                    if speech_defect_choice == "4":
                        try_again = False  # Выход из цикла, возврат к выбору языка
                        continue

                    etalon_words = []
                    if language_choice == "1":
                        if speech_defect_choice == "1":
                            etalon_words = ['Раушан', 'Картоп', 'Арпа']
                        elif speech_defect_choice == "2":
                            etalon_words = ['Шипа', 'Шалқар', 'Жарқын']
                        elif speech_defect_choice == "3":
                            etalon_words = ['Бала', 'Алмұрт', 'Шалбар',]
                    elif language_choice == "2":
                        if speech_defect_choice == "1":
                            etalon_words = ['Трактор', 'Раритет', 'Рулет']
                        elif speech_defect_choice == "2":
                            etalon_words = ['Саша', 'Шоссе', 'Шершавый']
                        elif speech_defect_choice == "3":
                            etalon_words = ['Мелочь', 'Лист', 'Капля']
                    else:
                        print("Некорректный выбор. Повторите попытку.")
                        continue

                    print("Режим выбран, произнесите слова:" if language_choice == "1" else "Выбран режим, произнесите слова:")
                    print("Осы сөздерді айтып көріңіз" if language_choice == "1" else "Попробуйте произнести эти слова:", ', '.join(etalon_words))
                    speak_words(etalon_words)

                    similarity_threshold = config["similarity_threshold"]
                    max_attempts = config["max_attempts"]
                    attempts = 0
                    correct_count = 0

                    while attempts < max_attempts:
                        data = stream.read(4096)
                        if recognizer.AcceptWaveform(data):
                            result = json.loads(recognizer.Result())
                            recognized_text = result["text"]
                            user_words = recognized_text.split()

                            # Внутри блока обработки попыток распознавания
                            for word in user_words:
                                word = word.strip('"')
                                max_similarity = max([similar(word, etalon_word) for etalon_word in etalon_words])
                                if max_similarity >= similarity_threshold:
                                    correct_count += 1
                                    if language_choice == "1":
                                        print(f"Сөз '{word}' сәтті анықталды!")
                                        save_recognition_result_to_file(language_choice, speech_defect_choice,
                                                                        word)  # Сохранение слова в файл
                                    else:
                                        print(f"Слово '{word}' успешно распознано!")
                                        save_recognition_result_to_file(language_choice, speech_defect_choice,
                                                                        word)  # Сохранение слова в файл
                                else:
                                    if language_choice == "1":
                                        print(f"Сөз, салыстырылған сөздермен сәйкес келмейді: '{word}'")
                                        save_recognition_result_to_file(language_choice, speech_defect_choice,
                                                                        word)  # Сохранение слова в файл
                                    else:
                                        print(f"Слово, не похожее на сравниваемые: '{word}'")
                                        save_recognition_result_to_file(language_choice, speech_defect_choice,
                                                                        word)  # Сохранение слова в файл

                            # Проверка на успешное произнесение всех слов
                            if correct_count == len(etalon_words):
                                print("Поздравляем, вы успешно произнесли все слова! Вы справились! " if language_choice == "2" else "Құттықтаймыз!Сіз барлық сөздерді дұрыс айттыңыз!Жарайсыз!")
                                if not return_to_main_menu(language_choice):
                                    return
                                try_again = False  # Выход из цикла
                                break

                            attempts += 1
                            if attempts == max_attempts:
                                print("Вы не смогли произнести правильно все слова. Попробуйте:" if language_choice == "2" else "Сіз көрсетілген сөздерді айта алмадыңыз.Келесіден таңдаңыз:")
                                print("1. Попробовать снова" if language_choice == "2" else "1. Қайтадан айтып көру")
                                print("2. Получить рекомендацию" if language_choice == "2" else "2. Анықтама алу")
                                print("3. Тілді қайтадан таңдау/Вернуться к выбору языка")
                                choice = input()
                                if choice == "2":
                                    handle_error(language_choice, speech_defect_choice)
                                    try_again = False  # Выход из цикла
                                    break
                                elif choice == "3":
                                    try_again = False  # Выход из цикла
                                    break
                                elif choice == "1":
                                    speech_defect_choice = None
                                    etalon_words = []

            except KeyboardInterrupt:
                print("Запись остановлена пользователем.")
            finally:
                stream.stop_stream()
                stream.close()
                mic.terminate()
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()