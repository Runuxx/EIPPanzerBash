# Installation von pyqt über die Konsole notwendig: "conda install pyqt"

from PyQt5.QtCore import Qt, QRect, QLine

from PyQt5.QtGui import QColor, QPainter, QPen

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from qtpy import QtGui, QtCore, QtWidgets


class MyRenderArea(QWidget):

   def paintEvent(self,e):
        painter = QPainter(self)
        painter.setBrush(QColor('white'))
        painter.setPen(Qt.NoPen)
        pen = QPen(QColor('red'))
        pen.setWidth(4)
        painter.setBrush(QColor('black'))
        painter.setPen(pen)
        rect = QRect(50,50,100,100)
        painter.drawRect(rect)
        painter.rotate(70)



class MyMainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(100,100,600,600)


        renderarea = MyRenderArea(self)
        self.setCentralWidget(renderarea)

        self.show()


app = QApplication([])
gui = MyMainWindow()
exit(app.exec_())
