import os
import json
import pyaudio
from vosk import Model, KaldiRecognizer
import pyttsx3
import sys
import threading
import io
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTextEdit, QPushButton, QLineEdit

# logoped_main.py functions
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
    main_window = MainWindowApp()
    main_window.show()

def return_to_language_selection(parent_window):
    parent_window.hide()  # Скрываем текущее окно
    lang_selection_window = LanguageSelectionWindowApp(parent_window)  # Передаем текущее окно
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

# MainWin.py functions and classes
class MainWindowApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow  # Сохраняем ссылку на главное окно
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 500)
        self.background_label = QtWidgets.QLabel(MainWindow)
        self.background_label.setGeometry(QtCore.QRect(0, 0, 700, 500))
        pixmap = QtGui.QPixmap('Fon.jpg')
        self.background_label.setPixmap(pixmap)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label1 = QtWidgets.QLabel(self.centralwidget)
        self.label1.setGeometry(QtCore.QRect(150, 50, 411, 41))
        self.label1.setLocale(QtCore.QLocale(QtCore.QLocale.Russian, QtCore.QLocale.Kazakhstan))
        self.label1.setTextFormat(QtCore.Qt.AutoText)
        self.label1.setAlignment(QtCore.Qt.AlignCenter)
        self.label1.setObjectName("label1")

        self.Button1 = QtWidgets.QPushButton(self.centralwidget)
        self.Button1.setGeometry(QtCore.QRect(280, 120, 111, 23))
        self.Button1.setObjectName("Button1")

        self.Button2 = QtWidgets.QPushButton(self.centralwidget)
        self.Button2.setGeometry(QtCore.QRect(280, 160, 111, 23))
        self.Button2.setObjectName("Button2")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Подключение сигнала к слоту
        self.Button1.clicked.connect(lambda: self.open_language_selection_window(MainWindow))
        self.Button2.clicked.connect(self.exit_program)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Главное окно"))
        self.label1.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:14pt;\">Добро пожаловать в программу Логопед!</span></p></body></html>"))
        self.Button1.setText(_translate("MainWindow", "Запустить"))
        self.Button2.setText(_translate("MainWindow", "Выйти/Шығу"))

    def exit_program(self):
        QtWidgets.qApp.quit()

    def open_language_selection_window(self, MainWindow):
        self.window = LanguageSelectionWindowApp(MainWindow)
        self.window.show()
        MainWindow.close()  # Закрываем главное окно

# language_selection_window.py functions and classes
class LanguageSelectionWindowApp(QtWidgets.QMainWindow):
    def __init__(self, previous_window=None):
        super().__init__()
        self.previous_window = previous_window
        self.setupUi(self)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 500)
        self.background_label = QtWidgets.QLabel(MainWindow)
        self.background_label.setGeometry(QtCore.QRect(0, 0, 700, 500))
        pixmap = QtGui.QPixmap('Fon.jpg') #Бұрынғы адрес: C:/Users/Public/Downloads/Diplon/Images/Fon.jpg'
        self.background_label.setScaledContents(True)  # Растягиваем изображение, чтобы оно помещалось в label
        self.background_label.setPixmap(pixmap)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(230, 30, 230, 50))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")

        self.pushButton_kz = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_kz.setGeometry(QtCore.QRect(200, 120, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_kz.setFont(font)
        self.pushButton_kz.setObjectName("pushButton_kz")
        self.pushButton_ru = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_ru.setGeometry(QtCore.QRect(200, 180, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_ru.setFont(font)
        self.pushButton_ru.setObjectName("pushButton_ru")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(200, 240, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 600, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Подключение сигналов к слотам
        self.pushButton_kz.clicked.connect(lambda: self.open_s3_window('1', MainWindow))
        self.pushButton_ru.clicked.connect(lambda: self.open_s3_window('2', MainWindow))
        self.pushButton_3.clicked.connect(QtWidgets.qApp.quit)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Выбор языка"))
        self.label.setText(_translate("MainWindow", "Тілді таңдаңыз/Выберите язык:"))
        self.pushButton_kz.setText(_translate("MainWindow", "Қазақ тілі"))
        self.pushButton_ru.setText(_translate("MainWindow", "Русский язык"))
        self.pushButton_3.setText(_translate("MainWindow", "Бағдарламадан шығу\nВыйти из программы"))

    def open_s3_window(self, language_choice, MainWindow):
        self.window = S3WindowApp(language_choice)
        self.window.show()
        MainWindow.close()

# S3.py functions and classes
class S3WindowApp(QtWidgets.QWidget):
    def __init__(self, language_choice):
        super().__init__()
        self.language_choice = language_choice
        self.setupUi(self)

    def setupUi(self, Form):
        self.language_choice = self.language_choice
        self.Form = Form  # Сохраняем ссылку на форму

        Form.setObjectName("Form")
        Form.resize(700, 500)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(0, 0, 700, 500))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("Fon.jpg"))
        self.label_2.setObjectName("label_2")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(120, 30, 451, 71))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(150, 120, 161, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(370, 120, 161, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(Form)
        self.pushButton_3.setGeometry(QtCore.QRect(150, 180, 161, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_4 = QtWidgets.QPushButton(Form)
        self.pushButton_4.setGeometry(QtCore.QRect(370, 180, 161, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setObjectName("pushButton_4")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        # Подключение сигналов к слотам
        self.pushButton.clicked.connect(lambda: self.start_logoped_main('1'))
        self.pushButton_2.clicked.connect(lambda: self.start_logoped_main('2'))
        self.pushButton_3.clicked.connect(lambda: self.start_logoped_main('3'))
        self.pushButton_4.clicked.connect(self.return_to_language_selection)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Тіл мүкістігін таңдау"))
        self.label.setText(_translate("Form", "Тіл мүкістігін таңдаңыз\nВыберите подходящий вариант:"))
        self.pushButton.setText(_translate("Form", "Ротацизм"))
        self.pushButton_2.setText(_translate("Form", "Сигматизм"))
        self.pushButton_3.setText(_translate("Form", "Ламбдацизм"))
        self.pushButton_4.setText(_translate("Form", "Тілді қайта таңдау\nВернуться к выбору языка"))

    def start_logoped_main(self, speech_defect_choice):
        t = threading.Thread(target=main, args=(self.language_choice, speech_defect_choice, self))
        t.start()

        # Открытие нового окна S4.py
        self.window = S4WindowApp(self.language_choice, speech_defect_choice)
        self.window.show()
        self.hide()  # Скрываем текущее окно

    def return_to_language_selection(self):
        self.hide()  # Скрываем текущее окно
        self.window = LanguageSelectionWindowApp(self)
        self.window.show()

# S4.py functions and classes
class S4WindowApp(QtWidgets.QMainWindow):
    def __init__(self, language_choice, speech_defect_choice):
        super().__init__()
        self.language_choice = language_choice
        self.speech_defect_choice = speech_defect_choice
        self.etalon_words = get_etalon_words(language_choice, speech_defect_choice)
        self.setupUi(self)
        self.init_console_redirect()
        self.previous_stdout = ""
        self.previous_stderr = ""

    def setupUi(self, S4Window):
        self.setObjectName("S4Window")
        self.resize(800, 600)

        self.background_label = QtWidgets.QLabel(self)
        self.background_label.setGeometry(QtCore.QRect(0, 0, 800, 600))
        pixmap = QtGui.QPixmap('Fon.jpg')
        self.background_label.setPixmap(pixmap)

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(180, 50, 441, 41))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")

        self.text_output = QTextEdit(self.centralwidget)
        self.text_output.setGeometry(QtCore.QRect(200, 120, 400, 200))
        self.text_output.setObjectName("text_output")

        self.command_input = QLineEdit(self.centralwidget)
        self.command_input.setGeometry(QtCore.QRect(200, 340, 300, 30))
        self.command_input.setObjectName("command_input")

        self.send_button = QPushButton("Отправить", self.centralwidget)
        self.send_button.setGeometry(QtCore.QRect(520, 340, 80, 30))
        self.send_button.clicked.connect(self.send_command)

        self.stop_button = QPushButton("Остановить", self.centralwidget)
        self.stop_button.setGeometry(QtCore.QRect(320, 380, 100, 40))
        self.stop_button.clicked.connect(self.stop_recognition)

        self.retranslateUi()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("S4Window", "Распознанные слова"))
        self.label.setText(_translate("S4Window", "Осы сөздерді айтып көріңіз\nПопробуйте произнести эти слова"))

    def init_console_redirect(self):
        sys.stdout = io.StringIO()  # Перенаправление стандартного вывода
        sys.stderr = io.StringIO()  # Перенаправление стандартного потока ошибок

        # Создаем таймер для периодического обновления вывода
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_console_output)
        self.timer.start(80)  # Обновление каждые 80 мс

    def update_console_output(self):
        sys.stdout.seek(0)  # Переходим в начало потока вывода
        sys.stderr.seek(0)  # Переходим в начало потока ошибок

        stdout_content = sys.stdout.read()  # Читаем вывод
        stderr_content = sys.stderr.read()  # Читаем ошибки

        # Проверяем, есть ли новые сообщения для вывода
        if stdout_content != self.previous_stdout or stderr_content != self.previous_stderr:
            # Обновляем текст в QTextEdit только если есть новые сообщения
            self.text_output.insertPlainText(stdout_content)
            self.text_output.insertPlainText(stderr_content)

            # Прокручиваем вниз, чтобы увидеть последние сообщения
            self.text_output.verticalScrollBar().setValue(self.text_output.verticalScrollBar().maximum())

            # Обновляем предыдущие значения для последующей проверки
            self.previous_stdout = stdout_content
            self.previous_stderr = stderr_content

    def send_command(self):
        command = self.command_input.text()
        if command:
            # Отправляем команду в logoped_main.py для обработки
            process_command(command, self.language_choice, self.speech_defект_choice, self)
            self.command_input.clear()

    def stop_recognition(self):
        self.running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.mic:
            self.mic.terminate()
        self.text_output.insertPlainText("Распознавание остановлено.\n")

    def closeEvent(self, event):
        # Здесь мы останавливаем любые запущенные процессы и закрываем приложение
        self.stop_recognition()
        QtWidgets.QApplication.quit()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MainWindowApp()
    MainWindow.show()
    sys.exit(app.exec_())
