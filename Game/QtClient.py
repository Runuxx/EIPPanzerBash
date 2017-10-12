from PyQt5.QtCore import Qt, QRect, QByteArray, QDataStream, QIODevice
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QWidget
from PyQt5.QtNetwork import QTcpSocket

# Kommentare analog zu QtServer.py







class MyRenderArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main = parent
        # Die Membervariable tcpSocket verwaltet den Kommunikationskanal zum Server.
        self.tcpSocket = QTcpSocket(self)
        # In der connectToHost-Routine muss die IP-Adresse des Servers eingetragen werden.
        # Hier steht zurzeit nur die localhost Adresse: 127.0.0.1
        self.tcpSocket.connectToHost('127.0.0.1',40890)
        self.tcpSocket.readyRead.connect(self.readData)
        self.mx = None
        self.my = None

    def readData(self):
        instr = QDataStream(self.tcpSocket)
        self.mx[0] = instr.readFloat()
        self.my[0] = instr.readFloat()
        self.update()

    def mousePressEvent(self, e):
        self.mx[1] = (e.x()-self.ox)/self.scale
        self.my[1] = (e.y()-self.oy)/self.scale
        block = QByteArray()
        out = QDataStream(block,QIODevice.ReadWrite)
        out.writeFloat(self.mx[1])
        out.writeFloat(self.my[1])
        self.tcpSocket.write(block)
        self.update()
        self.main.statusBar().showMessage("Maus−Press (" + str(e.x()) + "," + str(e.y()) + ")", 4000)


    def resizeEvent(self, e):
        if self.width() > self.height():
            self.scale = self.height()
            self.ox = (self.width() - self.height()) / 2
            self.oy = 0
        else:
            self.scale = self.width()
            self.ox = 0
            self.oy = (self.height() - self.width()) / 2
        if (self.mx == None):
            self.mx = [0.4,0.6]
            self.my = [0.5,0.5]

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setBrush(QColor('white'))
        painter.setPen(Qt.NoPen)
        rect = QRect(0, 0, self.width(), self.height())
        painter.drawRect(rect)
        painter.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen(QColor('black'))
        painter.setPen(pen)

        s = self.scale
        r = 0.1*s
        painter.setBrush(QColor('red'))
        rect = QRect(self.ox+s*self.mx[0]-r,self.oy+s*self.my[0]-r, 2*r, 2*r)
        painter.drawEllipse(rect)

        painter.setBrush(QColor('blue'))
        rect = QRect(self.ox+s*self.mx[1]-r,self.oy+s*self.my[1]-r, 2*r, 2*r)
        painter.drawEllipse(rect)

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 600, 600)

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction('Exit', self.close)

        renderarea = MyRenderArea(self)
        self.setCentralWidget(renderarea)

        statusbar = self.statusBar()
        statusbar.showMessage('Start', 1000)

        self.show()

app = QApplication([])
gui = MyMainWindow()
exit(app.exec_())
