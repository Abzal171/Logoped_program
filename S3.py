from PyQt5 import QtCore, QtGui, QtWidgets
import threading

class Ui_Form(object):
    def setupUi(self, Form, language_choice):
        self.language_choice = language_choice
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
        import logoped_main
        t = threading.Thread(target=logoped_main.main, args=(self.language_choice, speech_defect_choice))
        t.start()

        # Открытие нового окна S4.py
        from S4 import S4Window  # Импортируем S4 здесь, чтобы избежать циклического импорта
        self.Form.close()  # Закрываем текущее окно
        self.window = S4Window(self.language_choice, speech_defect_choice)
        self.window.show()

    def return_to_language_selection(self):
        # Импортируем модуль language_selection_window здесь, чтобы избежать циклического импорта
        import language_selection_window
        self.Form.close()  # Закрываем текущее окно
        self.window = QtWidgets.QMainWindow()
        self.ui = language_selection_window.Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.window.show()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form, "ru")  # Пример передачи языка, замените на реальные данные
    Form.show()
    sys.exit(app.exec_())