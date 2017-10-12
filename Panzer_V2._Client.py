from PyQt5.QtCore import Qt, QRect, QLine, QPoint, QByteArray, QDataStream, QIODevice, QTimer
from PyQt5.QtGui import QColor, QPainter, QPen, QImage ,QTransform
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtNetwork import QTcpServer, QHostAddress, QTcpSocket
import time, math


class MyRenderArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.background_tex = QImage("Ground.png")
        self.ups = 30
        self.players_tex = [QImage("panzer_0.png"), QImage("panzer_1.png"), QImage("panzer_2.png")]
        self.players = [Player(self.ups, (0, 0))]
        self.player_count = 1
        self.controls = [False, False, False, False, False]
        self.game_data = ["0#0#0.5#0.5#5"]
        self.connected = False

        # Die Membervariable tcpSocket verwaltet den Kommunikationskanal zum Server.
        self.tcpSocket = QTcpSocket(self)
        # In der connectToHost-Routine muss die IP-Adresse des Servers eingetragen werden.
        # Hier steht zurzeit nur die localhost Adresse: 127.0.0.1
        self.tcpSocket.connectToHost('134.93.86.201', 40891)
        self.tcpSocket.readyRead.connect(self.readData)

    def readData(self):
        instr = QDataStream(self.tcpSocket)
        raw_data = instr.readQString()

        if raw_data != "":
            self.writeData()
            self.update()

        data = raw_data.split("p")

        if len(data) > 1:
            del data[0]
            self.game_data = data

        diff = len(data) - self.player_count

        if diff > 0:
            for i in range(0,diff):
                self.spawnPlayer()
                self.player_count += 1

    def writeData(self):
        block = QByteArray()
        out = QDataStream(block, QIODevice.ReadWrite)
        controls = ""
        for b in self.controls:
            if b:
                controls += "1"
            else:
                controls += "0"
        #print("OUT: ", controls)
        out.writeQString(controls)
        self.tcpSocket.write(block)


    def keyPressEvent(self, e):
        if e.key() == Qt.Key_W or e.key() == Qt.Key_Up:
            self.controls[0] = True
        if e.key() == Qt.Key_S or e.key() == Qt.Key_Down:
            self.controls[1] = True
        if e.key() == Qt.Key_A or e.key() == Qt.Key_Left:
            self.controls[2] = True
        if e.key() == Qt.Key_D or e.key() == Qt.Key_Right:
            self.controls[3] = True
        #self.writeData()


    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key_W or e.key() == Qt.Key_Up:
            self.controls[0] = False
        if e.key() == Qt.Key_S or e.key() == Qt.Key_Down:
            self.controls[1] = False
        if e.key() == Qt.Key_A or e.key() == Qt.Key_Left:
            self.controls[2] = False
        if e.key() == Qt.Key_D or e.key() == Qt.Key_Right:
            self.controls[3] = False
        #self.writeData()

    def spawnPlayer(self):
        self.players.append(Player(self.ups, (0.5, 0.5)))

    def resizeEvent(self, e):
        # (ox,oy) steht für die linke obere Ecke des quadratischen Spielfeldes und dient als
        # Ursprung des Koordinatensystems.
        if self.width() > self.height():
            self.len = self.height()
            self.ox = (self.width() - self.height()) / 2
            self.oy = 0
        else:
            self.len = self.width()
            self.ox = 0
            self.oy = (self.height() - self.width()) / 2
        self.tex_scale = self.len/self.background_tex.width()

    def draw_players(self):
        painter = QPainter(self)
        index = 0
        for player in self.players:
            painter.save()
            tex = self.players_tex[index]
            trans = QTransform()
            (x, y) = player.get_position()
            size = tex.width()*self.tex_scale
            trans.translate(self.ox+x*self.len, (self.oy+y*self.len))
            trans.rotate(-player.get_rotation()/2)
            trans.translate(0 - size/2, 0 - size/2)
            painter.setTransform(trans)
            painter.drawImage(0, 0, tex.scaled(size, size))
            painter.restore()
            index += 1

    def position_players(self):
        index = 0
        for player in self.players:
            player.position_player(self.game_data[index])
            index += 1

    def paintEvent(self,e):
        painter = QPainter(self)
        painter.setBrush(QColor('black'))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, self.width(), self.height())
        painter.drawImage(self.ox, self.oy, self.background_tex.scaled(self.len, self.len))
        self.position_players()
        self.draw_players()
        self.readData()


class Player():
    def __init__(self, ups, position, rotation=0):
        self.x = position[0]
        self.y = position[1]
        self.r = rotation
        self.id = ""

    def position_player(self, raw_data):
        #print("raw", raw_data)
        data = raw_data.split("#")
        self.x = float(data[2])
        self.y = float(data[3])
        self.r = float(data[4])


    def get_position(self):
        return (self.x, self.y)

    def get_rotation(self):
        return self.r




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