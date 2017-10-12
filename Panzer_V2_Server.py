from PyQt5.QtCore import Qt, QRect, QLine, QPoint, QByteArray, QDataStream, QIODevice, QTimer
from PyQt5.QtGui import QColor, QPainter, QPen, QImage ,QTransform ,QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtNetwork import QTcpServer, QHostAddress
import time, math


class MyRenderArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.main = parent
        self.background_tex = QImage("Ground.png")
        self.ups = 60
        self.uc = 0
        self.gamesecond = 0
        self.players_tex = [QImage("panzer_0.png"), QImage("panzer_1.png"), QImage("panzer_2.png")]
        self.explosion_sprites = [QImage("000" + str(i) + ".png") for i in range(1,10)] + [QImage("00"+str(i)+".png") for i in range(10,51)]
        self.players = [Player(self.ups, (0.5, 0.5)),Player(self.ups, (0.7, 0.7))]
        self.controls = [False, False, False, False, False]
        self.controls2 = [False, False, False, False, False]
        self.inputs = [self.controls,self.controls2]

        self.timer = QTimer()
        # Wir richten einen Server ein, zu dem Clients einen Kommunikationskanal
        # öffnen können.
        self.tcpServer = QTcpServer(self)
        # Der Server akzeptiert jeden Client, der auf der angegebenen Port-Nummer
        # sendet.
        self.tcpServer.listen(QHostAddress.Any, 40890)
        # self.tcpServer.listen(QHostAddress('127.0.0.1'), 40890)

        # Falls beim Server eine Verbindungsanfrage von einem Client eingeht,
        # soll die eigene Memberfunktion connectToClient aufgerufen werden.
        self.tcpServer.newConnection.connect(self.connectToClient)
        # Falls ein Fehler beim Server auftritt, kann dieser mit
        # self.tcpServer.errorString() abgefragt werden.

        # Memberfunktion für eine Verbindungsanfrage eines Clients




    def timer_funktion(self):
        self.writeData()
        self.update()


    def connectToClient(self):
        # Über die Membervariable tcpSocket kann der Kommunikationskanal zum
        # Senden und Empfangen von Nachrichten angesprochen werden.
        self.tcpSocket = self.tcpServer.nextPendingConnection()
        # In der Statuszeile geben wir aus, dass sich ein Client mit dem Server
        # verbunden hat.
        self.main.statusBar().showMessage('Client connected')
        self.connected = True
        # Falls neue Daten zum Lesen vom Client eingetroffen sind, soll die
        # Memberfunktion readData aufgerufen werden.
        self.tcpSocket.readyRead.connect(self.readData)

        self.timer.timeout.connect(self.timer_funktion)
        self.timer.start(round(1000/self.ups))


    def readData(self):
        instr = QDataStream(self.tcpSocket)
        data = instr.readQString()
        #print(data)
        controls = [False, False, False, False, False]
        for i in range(len(data)):
            if data[i] == "1":
                self.controls2[i] = True
            else:
                self.controls2[i] = False


    def encode_game(self):
        data = ""
        player_index = 0
        #Format: pNUMMER#USED#POSX#POSY#ROT
        for player in self.players:
            pos = player.get_position()
            data += "p" + str(player_index) + "#" + "0" + "#" + str(pos[0]) + "#" + str(pos[1]) + "#" + str(player.get_rotation())

        return data



    def writeData(self):
        block = QByteArray()
        out = QDataStream(block, QIODevice.ReadWrite)
        controls = ""
        data = self.encode_game()
        out.writeQString(data)
        print(data)
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

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key_W or e.key() == Qt.Key_Up:
            self.controls[0] = False
        if e.key() == Qt.Key_S or e.key() == Qt.Key_Down:
            self.controls[1] = False
        if e.key() == Qt.Key_A or e.key() == Qt.Key_Left:
            self.controls[2] = False
        if e.key() == Qt.Key_D or e.key() == Qt.Key_Right:
            self.controls[3] = False

    def spawnPlayer(self):
        self.players.append(Player((0.5, 0.5)))

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
            self.draw_explosion(self.ox+x*self.len, (self.oy+y*self.len))
            painter.restore()
            index += 1


    def draw_explosion(self, x, y):
        painter = QPainter(self)
        frame = int(self.gamesecond*50)
        size = self.explosion_sprites[0].width()*self.tex_scale
        painter.drawImage(x - size/2, y-size/2,
                          self.explosion_sprites[frame].scaled(size, size))

    def move_players(self):
        index = 0
        for player in self.players:
            player.move(self.inputs[index])

            index += 1

    def paintEvent(self,e):
        painter = QPainter(self)
        painter.setBrush(QColor('black'))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, self.width(), self.height())
        painter.drawImage(self.ox, self.oy, self.background_tex.scaled(self.len, self.len))
        self.move_players()
        self.draw_players()
        self.uc += 1
        if self.uc == self.ups:
            self.uc = 0
        self.gamesecond = self.uc/self.ups



class Player():
    def __init__(self, ups, position, rotation=0):
        self.x = position[0]
        self.y = position[1]
        self.r = rotation
        self.a = 0
        self.r_speed = 10 * (60/ups)
        self.max_speed = 0.01 * (60/ups)

    def get_position(self):
        return (self.x, self.y)

    def get_rotation(self):
        return self.r

    def move(self,inputs):
        up = inputs[0]
        down = inputs[1]
        left = inputs[2]
        right = inputs[3]
        shoot = inputs[4]

        if up:
            self.a = -1
        if down:
            self.a = 1
        if right:
            self.r -= self.r_speed
        if left:
            self.r += self.r_speed

        self.y += math.cos(self.r / 360 * math.pi) * self.max_speed * self.a
        self.x += math.sin(self.r / 360 * math.pi) * self.max_speed * self.a

        if not up and not down:
            self.a *= round(0.9, 5)

        if self.x > 1:
            self.x = 0
        if self.x < 0:
            self.x = 1
        if self.y > 1:
            self.y = 0
        if self.y < 0:
            self.y = 1

class MyMainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(800,100,600,600)

        renderarea = MyRenderArea(self)
        self.setCentralWidget(renderarea)

        # Anlegen einer Statuszeile am unteren Rand des QMainWindow.
        statusbar = self.statusBar()
        # Anzeigen eines Textes in der Statuszeile für eine Sekunde.
        statusbar.showMessage('Start', 1000)

        self.show()


app = QApplication([])
gui = MyMainWindow()
exit(app.exec_())