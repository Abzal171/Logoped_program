from PyQt5 import QtCore, QtGui, QtWidgets
import S3

class Ui_MainWindow(object):
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
        self.window = QtWidgets.QWidget()
        self.ui = S3.Ui_Form()
        self.ui.setupUi(self.window, language_choice)
        self.window.show()
        MainWindow.close()