from vosk import Model, KaldiRecognizer
import pyaudio

def similar(a, b):
    # Простой метод сравнения схожести слов (можно заменить на более сложный)
    return sum([1 for char_a, char_b in zip(a, b) if char_a == char_b]) / max(len(a), len(b))

def main():
    print("Каким языком вы говорите?")
    print("1. Казахский")
    print("2. Русский")
    language_choice = input().strip()

    if language_choice == "1":
        model_path = r'C:\Users\Public\Downloads\Diplon\lang_model\kz_small'
        print("Выбран режим для казахского языка.")
    elif language_choice == "2":
        model_path = r'C:\Users\Public\Downloads\Diplon\lang_model\ru_small'
        print("Выбран режим для русского языка.")
    else:
        print("Некорректный выбор. Завершение программы.")
        return

    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
    stream.start_stream()

    try:
        print("Начинается запись и распознавание. Для остановки введите 'остановка'.")

        if language_choice == "1":
            etalon_words = ['трактор', 'раритет', 'рюрик']
        elif language_choice == "2":
            print("Какой дефект речи у вас?")
            print("1. Картавость")
            print("2. Шепелявость")
            speech_defect_choice = input().strip()
            if speech_defect_choice == "1":
                etalon_words = ['трактор', 'раритет', 'рюрик']  # Замените на свои эталонные слова для картавящих
                print("Выбран режим для картавящих, говорите.")
            elif speech_defect_choice == "2":
                etalon_words = ['слово4', 'слово5', 'слово6']  # Замените на свои эталонные слова для шепелявых
                print("Выбран режим для шепелявящих, говорите.")
            else:
                print("Некорректный выбор. Завершение программы.")
                return

        similarity_threshold = 0.7  # Пороговое значение для схожести слов

        while True:
            data = stream.read(4096)
            if recognizer.AcceptWaveform(data):
                recognized_text = recognizer.Result()[14:-3]
                user_words = recognized_text.split()

                for word in user_words:
                    max_similarity = max([similar(word, etalon_word) for etalon_word in etalon_words])
                    if max_similarity >= similarity_threshold:
                        print(f"Слово '{word}' успешно распознано!")
                    else:
                        print(f"Слово, не похожее на сравниваемые: '{word}'")

                if "остановка" in recognized_text:
                    print("Распознано триггерное слово 'остановка'. Завершение программы.")
                    break

    except KeyboardInterrupt:
        print("Запись остановлена пользователем.")
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()

if __name__ == "__main__":
    main()