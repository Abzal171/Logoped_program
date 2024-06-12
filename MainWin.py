from PyQt5 import QtCore, QtGui, QtWidgets
import language_selection_window

class Ui_MainWindow(object):
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
        self.Button1.setText(_translate("MainWindow", "Қосу/Запуск"))
        self.Button2.setText(_translate("MainWindow", "Выйти/Шығу"))

    def exit_program(self):
        QtWidgets.qApp.quit()

    def open_language_selection_window(self, MainWindow):
        self.window = QtWidgets.QMainWindow()
        self.ui = language_selection_window.Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.window.show()
        MainWindow.close()  # Закрываем главное окно

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())