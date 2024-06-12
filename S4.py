import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTextEdit, QPushButton, QLineEdit
from logoped_main import get_etalon_words, process_command
import io

class S4Window(QtWidgets.QMainWindow):
    def __init__(self, language_choice, speech_defect_choice):
        super().__init__()
        self.language_choice = language_choice
        self.speech_defect_choice = speech_defect_choice
        self.etalon_words = get_etalon_words(language_choice, speech_defect_choice)
        self.setupUi()
        self.init_console_redirect()
        self.previous_stdout = ""
        self.previous_stderr = ""

    def setupUi(self):
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
            process_command(command, self.language_choice, self.speech_defect_choice, self)
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
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <language_choice> <speech_defект_choice>")
        sys.exit(1)
    language_choice = sys.argv[1]
    speech_defect_choice = sys.argv[2]
    app = QtWidgets.QApplication(sys.argv)
    ex = S4Window(language_choice, speech_defect_choice)
    ex.show()
    sys.exit(app.exec_())
