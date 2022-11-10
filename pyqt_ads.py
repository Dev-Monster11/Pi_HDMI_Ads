
import cv2
import json
import time
import sys
from screeninfo import get_monitors
import urllib.request
import numpy as np
import random

from PyQt5.QtCore import QTimer, QThread, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import QLabel, QApplication, QDialog, QGraphicsOpacityEffect
from PyQt5.QtGui import QImage, QPixmap, QPainter
from camera import CameraBackend

screen = get_monitors()[0]
width = screen.width
height = screen.height


class MainDlg(QDialog):
    def __init__(self):
        super(MainDlg, self).__init__()
        self.config = self.loadConfig()
        self.camera = cv2.VideoCapture(0)
        self.frame = np.zeros((width, height, 3), dtype = "uint8")
        self.content = np.zeros((width, height, 3), dtype="uint8")
        self.start = time.time()

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateFrame)

        self.showTimer = QTimer()
        self.showTimer.timeout.connect(self.showContent)
        self.showTimer.start(self.config['period'] * 1000)

        self.hideTimer = QTimer()
        self.hideTimer.timeout.connect(self.hideContent)
        self.hideTimer.setSingleShot(True)

        self.contentShow = False

        self.timer.start(40)
        # self.startFlag = False

        self.content = QLabel(self)
        # self.content.setGeometry(0, 0, 0, 0)
        self.content.setStyleSheet('background-color: transparent')
        if (self.config['layout'] == 'left_50'):
            self.content.setGeometry(0, 0, int(width * 0.5), height)
        elif (self.config['layout'] == 'right_50'):
            self.content.setGeometry(int(width * 0.5), 0, width, height)
        elif (self.config['layout'] == 'top_10'):
            self.content.setGeometry(0, 0, width, int(height * 0.1))
        elif (self.config['layout'] == 'bottom_10'):
            self.content.setGeometry(0, int(height * 0.9), width, height)
        self.content.show()
        fade_effect = QGraphicsOpacityEffect(self);
        self.content.setGraphicsEffect(fade_effect);
        self.animation = QPropertyAnimation(fade_effect, b"opacity");

    def hideContent(self):
        # self.showContent = False
        print('hide')
        
        self.animation.setEasingCurve(QEasingCurve.InOutQuad);
        self.animation.setDuration(1500);
        self.animation.setStartValue(1);
        self.animation.setEndValue(0.01);
        self.animation.start()
        # self.animation.start(QPropertyAnimation.DeleteWhenStopped);
        self.content.hide()
    def showContent(self):
        
        index = random.randint(0, len(self.config['contents']) - 1)

        data = self.config['contents'][index]
        if (data['AdType'] == 'IMAGE'):
            url_response = urllib.request.urlopen(data['AdPath'])
            contentFrame = cv2.imdecode(np.array(bytearray(url_response.read()), dtype=np.uint8), -1)

            contentFrame = cv2.resize(contentFrame, (self.content.width(), self.content.height()))

        # if self.config['layout'] == 'left_50' or self.config['layout'] == 'right_50':
        #     contentFrame = cv2.resize(contentFrame, (int(width*0.5), height))
        # else:
        #     contentFrame = cv2.resize(contentFrame, (int(width*0.1), height))
            frame = cv2.cvtColor(contentFrame, cv2.COLOR_BGR2RGB)
            h, w, _ = frame.shape
            bg = QImage(frame.data, w, h, w * 3 ,QImage.Format_RGB888)
            self.content.setPixmap(QPixmap.fromImage(bg))

            self.animation.setEasingCurve(QEasingCurve.InOutQuad);
            self.animation.setDuration(1500);
            self.animation.setStartValue(0.01);
            self.animation.setEndValue(1);
            self.animation.start()
            # self.animation.start(QPropertyAnimation.DeleteWhenStopped);

            self.hideTimer.start(data['AdDuration'] * 1000 + 1500 * 2)
        # self.content = contentFrame
        # self.contentExist = True
        # self.contentIndex = self.contentIndex + 1
        # self.changeContentTimer.start(self.seconds[self.contentIndex] * 1000)
 

    def paintEvent(self, event):
        painter = QPainter(self)
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape
        bg = QImage(frame.data, w, h, w * 3 ,QImage.Format_RGB888)
        bg = bg.scaled(width, height)
        painter.drawImage(0, 0, bg)
    def loadConfig(self):
        with open('config.json', 'r') as config_file:
            configData = json.load(config_file)
            return configData

    def updateFrame(self):

        ret, self.frame = self.camera.read()
        self.startFlag = ret

        # now = time.time()
        # delta = (int(now - tempStart / 1000)) % self.seconds[len(seconds) - 1]

        # index = 0
        # for x in seconds:
        #     if (delta < x):
        #         break
        #     index = index + 1
        # data = config['contents'][index - 1]
        # if (data['AdType'] == 'IMAGE'):

        #     url_response = urllib.request.urlopen(data['AdPath'])
        #     contentFrame = cv2.imdecode(np.array(bytearray(url_response.read()), dtype=np.uint8), -1)
        #     if (config['layout'] == 'left_50' or config['layout'] == 'right_50'):
        #         contentFrame = cv2.resize(contentFrame, (int(width*0.5), height))
        #     else:
        #         contentFrame = cv2.resize(contentFrame, (int(width*0.1), height))
        # elif (data['AdType'] == 'VIDEO'):

        # elif (data['AdType'] == 'SCROLL'):
        #     url_response = urllib.request.urlopen(data['AdPath'])
        #     contentFrame = cv2.imdecode(np.array(bytearray(url_response.read()), dtype=np.uint8), -1)

        self.repaint()    
    def releaseAll(self):
        self.timer.stop()
        self.camera.release()
        exit(0)
    def keyPressEvent(self, event):
        if event.key() == 'q':
            self.releaseAll()       




def main():
    app = QApplication(sys.argv)
    mainDlg = MainDlg()
    mainDlg.showFullScreen()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()