#!/usr/bin/env python3
import sys
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QThread, pyqtSignal
from Widget import Ui_Form
from pyaudio import PyAudio
from queue import Queue
from time import sleep
import cv2
import socket
import pickle

# python -m PyQt5.uic.pyuic -x widget.ui -o main_cmd.py
# pip install auto-py-to-exe
# pyinstaller Main.py --noconsole --onefile --paths "C:\Users\SSAFY\anaconda3\lib\site-packages\cv2"

class SendAudioThread(QThread):
    def __init__(self, data):
        super().__init__()
        self._data_ = data
        self._flag_ = True

    def run(self):
        p = PyAudio()
        stream = p.open(format=p.get_format_from_width(2),
                            channels=1,
                            rate=44100,
                            input=True)
        while self._flag_:
            frame = stream.read(4410)

            self._data_.append(frame)
            print(len(self._data_))


class SendThread(QThread):
    finished = pyqtSignal()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 500000)

    def __init__(self, img_label, data):
        super().__init__()
        self.img_label = img_label
        self._flag_ = True
        self._data_ = data

    def setHost(self, host):
        self.host = host
    
    def run(self):
        video_capture = cv2.VideoCapture(0)
        while self._flag_:
            try:
                img, frame = video_capture.read()
                if not img:
                    print("no img")
                    continue

                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.img_label.setPixmap(QPixmap.fromImage(image))

                ret, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY),30])
                message = pickle.dumps([buffer, b"".join(self._data_)])
                print(len(message))
                self._data_.clear()
                self.client_socket.sendto(message, self.host)

            except BlockingIOError:
                continue
            except:
                print("send")
                continue

        self.finished.emit()

class RecvAudioThread(QThread):
    def __init__(self, q):
        super().__init__()
        self._flag_ = True
        self._q_ = q

    def run(self):
        p = PyAudio()
        stream = p.open(format=p.get_format_from_width(2),
                            channels=1,
                            rate=44100,
                            output=True)
        while self._flag_:
            buffer = self._q_.get()
            stream.write(buffer)


class RecvThread(QThread):
    finished = pyqtSignal()
    
    def __init__(self, img_label, q):
        super().__init__()
        self.img_label = img_label
        self._flag_ = True
        self._q_ = q

    def setHost(self, host):
        host_name = socket.gethostname()
        self.host = (socket.gethostbyname(host_name), host[1])

    def run(self):
        print(self.host)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(self.host)
        server_socket.setblocking(False)
        
        #video_capture = cv2.VideoCapture(0)
        while self._flag_:
            try:
                packet, newHost = server_socket.recvfrom(500000)
                buffer = pickle.loads(packet)
                img = cv2.imdecode(buffer[0], cv2.IMREAD_COLOR)
                self._q_.put(buffer[1])
                rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.img_label.setPixmap(QPixmap.fromImage(image))
            except BlockingIOError:
                continue
            except:
                print("recv")
                continue

        self.finished.emit()

# from PyQt5 import uic
# form_class = uic.loadUiType("widget.ui")[0]
# 1024, 600
# class MainApp(QtWidgets.QMainWindow, form_class):
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.Form = Ui_Form()
        self.Form.setupUi(self)
        self._clickedFlag_ = True
        self._q_ = Queue()
        self._data_ = []
        self.recvThread = RecvThread(self.Form.CameraFrame, self._q_)
        self.sendThread = SendThread(self.Form.CameraFrame_2, self._data_)
        self.recvAudioThread = RecvAudioThread(self._q_)
        self.sendAudioThread = SendAudioThread(self._data_)

    def changeFlag(self, state):
        if state:
            self.recvAudioThread._flag_ = True
            self.recvThread._flag_ = True
            self.sendAudioThread._flag_ = True
            self.sendThread._flag_ = True
        else:
            self.recvAudioThread._flag_ = False
            self.recvThread._flag_ = False
            self.sendAudioThread._flag_ = False
            self.sendThread._flag_ = False

    def clickedBtn(self):
        if self._clickedFlag_:
            host = self.Form.getHost()
            self.recvThread.setHost(host)
            self.sendThread.setHost(host)
            self.changeFlag(True)
            
            try:
                self.recvAudioThread.start()
                self.recvThread.start()
                sleep(1)
                self.sendThread.start()
                self.sendAudioThread.start()
            except:
                print("Ads?")

            self.Form.pushButton.setText("해 제")
            self.Form.ConnectState.setText("연결 상태 : True")

            print("연 결")
            self._clickedFlag_ = False
        else:
            self.changeFlag(False)
            self.Form.pushButton.setText("연 결")
            self.Form.ConnectState.setText("연결 상태 : False")

            print("해 제")
            self._clickedFlag_ = True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = app.desktop().screenGeometry()
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
