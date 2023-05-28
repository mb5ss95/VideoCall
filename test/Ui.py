#!/usr/bin/env python3
from PyQt5 import QtCore, QtGui, QtWidgets

#1024, 600

class myButton(QtWidgets.QPushButton):
    def __init__(self, me, callback):
        super().__init__(me)
        self.setText("통화 시작")
        font = self.font()
        font.setPointSize(80)
        self.setFont(font)
        # self.setGeometry(QtCore.QRect(24 , 24, 976, 556))
        self.clicked.connect(callback)
        # self.setStyleSheet("background-image : url(views/btnSend.png);\
        #                                background-repeat : no-repeat;")

class myInput(QtWidgets.QInputDialog):
    def __init__(self, me):
        super().__init__(me)
    

class Form(QtWidgets.QWidget):
    def __init__(self, me, callback):
        super().__init__()
        
        size = [me.width(), me.height()]
        self.input = myInput(self)
        self.pushButton = myButton(self, callback)
        self.input.setGeometry(0, 0, size[0], size[1]*0.7)
        self.pushButton.setGeometry(0, size[1]*0.7, size[0], size[1]*0.2)
        

class Form2(QtWidgets.QWidget):
    def __init__(self, me):
        super().__init__(me)

        movie = QtGui.QMovie("views/defaultState.gif")
        self.label = QtWidgets.QLabel(self)
        self.label.move(0, 0)
        movie.setScaledSize(me.sizeHint().scaled(1024, 400, QtCore.Qt.AspectRatioMode(1)))
        self.label.setMovie(movie)

        movie2 = QtGui.QMovie("views/waiting.gif")
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.move(0, 400)
        movie2.setScaledSize(me.sizeHint().scaled(1024, 200, QtCore.Qt.AspectRatioMode(1)))
        self.label_2.setMovie(movie2)

        movie.start()
        movie2.start()

