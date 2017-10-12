"""Game of Fabian Peters, Tim Heussler, Till Goebel, Taner Celik"""

from PyQt5.QtCore import Qt, QRect, QLine, QPoint, QTimer, QByteArray, QDataStream, QIODevice
from PyQt5.QtGui import QColor, QPainter, QPen, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMenu
from PyQt5.QtNetwork import QTcpServer, QHostAddress
import math, random

from PyQt5 import QtGui


class Ball():
    def __init__(self, velx, vely, x, y, width, height, ID):
        self.velx = velx
        self.vely = vely
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.life = 10000
        self.ID = ID
        print(self.ID)



    def move(self):
        self.life -= 1
        self.y += self.vely
        self.x += self.velx
        if self.x > self.width:
            self.velx = -self.velx
        if self.y > self.height:
            self.vely = -self.vely
        if self.x < 0:
            self.velx = -self.velx
        if self.y < 0:
            self.vely = -self.vely

    def getLife(self):
        return self.life

    def hitX(self):
        self.velx *= -1
    def hitY(self):
        self.vely *= -1

    def getY(self):
        return self.y

    def getX(self):
        return self.x


class Wall():
    def __init__(self, x, y, seite, height, width, ox, oy, len):
        self.width = width
        self.height = height
        self.seite = seite
        self.x = x
        self.y = y
        self.draw(ox, oy, len)

    def draw(self, ox, oy, len):
        if self.seite == 4:
            self.points = QPoint(ox + len * self.x, oy + len * self.y)
            self.pointe = QPoint(ox + len * self.x,oy + len *  (self.y + self.height / 4))
        if self.seite == 1:
            self.points = QPoint(ox + len * self.x, oy + len * self.y)
            self.pointe = QPoint(ox + len * (self.x + self.width / 4), oy + len * self.y)
        if self.seite == 2:
            self.points = QPoint(ox + len * (self.x + self.width / 4), oy + len * self.y)
            self.pointe = QPoint(ox + len * (self.x + self.width / 4), oy + len * (self.y + self.height / 4))
        if self.seite == 3:
            self.points = QPoint(ox + len * self.x, oy + len * (self.y + self.height / 4))
            self.pointe = QPoint(ox + len * (self.x + self.width / 4), oy + len * (self.y + self.height / 4))



    def getSeite(self):
        return self.seite

class Player():
    def __init__(self, ID):
        self.keyDown = [False, False, False, False, False]
        self.ID = ID
        self.velx = 0
        self.vely = 0
        self.winkel = 0
        self.winkelnext = 0
        self.alive = True
        self.ballcount = 0
        if ID == 1:
            self.x = 0.1
            self.y = 0.1
            self.color = 'yellow'

        if ID == 2:
            self.x = 0.9
            self.y = 0.9
            self.color = 'blue'




class MyRenderArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Das Zeichenfeld muss den Focus für KeyPress-Events erhalten.
        self.setFocusPolicy(Qt.StrongFocus)
        # Wir laden eine png-Datei (mit Transparenz) und skalieren das Bild
        # auf die gewünschte Größe.
        self.background_tex = QImage("Ground.png")
        self.players_tex = [QImage("panzer_0.png"), QImage("panzer_1.png"), QImage("panzer_2.png")]
        self.explosion_sprites = [QImage("000" + str(i) + ".png") for i in range(1, 10)] + [
            QImage("00" + str(i) + ".png") for i in range(10, 51)]

        self.main = parent
        self.lebendig = True
        self.alive = False
        self.point = QPoint(0, 0)
        self.pointl = QPoint(0, 0)
        self.balls = []
        self.ballsize = 15
        self.image = QImage('Pacman.png').scaled(100, 100)
        self.x = 100
        self.y = 100
        self.velx = 0
        self.vely = 0
        self.winkel = 0
        self.winkelnext = 0
        self.players = []
        self.ballcount1 = 0
        self.ballcount2 = 0
        self.score1 = 0
        self.score2 = 0

        self.level_id = 0
        self.wallscoordinates = []
        self.walls = []
        self.wallsbuild = False
        self.run = True
        self.ups = 60
        self.connected = False
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
        if self.connected:
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
        self.timer.start(round(1000 / self.ups))

    def readData(self):
        instr = QDataStream(self.tcpSocket)
        data = instr.readQString()
        print(data)
        for i in range(len(data)):
            if data[i] == "1":
                self.players[1].keyDown[i] = True
            else:
                self.players[1].keyDown[i] = False
        #print("KEYREADOUT", self.players[1].keyDown)


    def encode_game(self):
        data = ""
        player_index = 1
        # Format: pID#POSX#POSY#ROT
        for player in self.players:
            pos = (player.x, player.y)
            data += "p" + str(player_index) + "#" + "0" + "#" + str(round(pos[0], 4)) + "#" + str(round(pos[1], 4)) + "#" + str(round(
                player.winkel, 4))
            player_index += 1
        data += "l" + str(self.level_id)
        return data

    def writeData(self):
        block = QByteArray()
        out = QDataStream(block, QIODevice.ReadWrite)
        data = self.encode_game()
        print(data)
        out.writeQString(data)
        self.tcpSocket.write(block)

    def getRun(self):
        return self.run

    def setRun(self,run):
        self.run = run


    # Memberfunktion zur Handhabung von KeyPress-Events
    def keyPressEvent(self, e: QtGui.QKeyEvent):
        for i in self.players:

            if i.ID == 1:
                if e.key() == Qt.Key_W:
                    i.keyDown[0] = True
                if e.key() == Qt.Key_S:
                    i.keyDown[1] = True
                if e.key() == Qt.Key_A:
                    i.keyDown[2] = True
                if e.key() == Qt.Key_D:
                    i.keyDown[3] = True
                if e.key() == Qt.Key_V:
                    i.keyDown[4] = True

            '''
            if i.ID == 2:
                if e.key() == Qt.Key_Up:
                    i.keyDown[0] = True
                if e.key() == Qt.Key_Down:
                    i.keyDown[1] = True
                if e.key() == Qt.Key_Left:
                    i.keyDown[2] = True
                if e.key() == Qt.Key_Right:
                    i.keyDown[3] = True
                if e.key() == Qt.Key_M:
                    if self.ballcount2 < 6:
                        self.ballcount2 += 1
                        self.spawnBall(i.winkel, i.x, i.y, i.ID)
                    else: pass
            '''

        if e.key() == Qt.Key_G:
            self.run = False


    def keyReleaseEvent(self, e):
        for i in self.players:
            if i.ID == 1:
                if e.key() == Qt.Key_W:
                    i.keyDown[0] = False
                if e.key() == Qt.Key_S:
                    i.keyDown[1] = False
                if e.key() == Qt.Key_A:
                    i.keyDown[2] = False
                if e.key() == Qt.Key_D:
                    i.keyDown[3] = False

            if i.ID == 2:
                if e.key() == Qt.Key_Up:
                    i.keyDown[0] = False
                if e.key() == Qt.Key_Down:
                    i.keyDown[1] = False
                if e.key() == Qt.Key_Left:
                    i.keyDown[2] = False
                if e.key() == Qt.Key_Right:
                    i.keyDown[3] = False



    def playerMovment(self):
        for i in self.players:
            print(i.ID, i.keyDown)
            max_speed = 0.004

            if i.keyDown[0]:
                i.velx = (math.cos(i.winkel) * max_speed)
                i.vely = (math.sin(i.winkel) * max_speed)
            if i.keyDown[1]:
                i.velx = (math.cos(i.winkel) * max_speed)
                i.vely = (math.sin(i.winkel) * max_speed)
            if i.keyDown[2]:
                i.winkelnext = - 0.05
            if i.keyDown[3]:
                i.winkelnext = + 0.05
            if i.keyDown[4]:
                i.keyDown[4] = False
                if i.ballcount < 6:
                    i.ballcount += 1
                    self.spawnBall(i.winkel, i.x, i.y, i.ID)
                else:
                    pass

            if i.keyDown[0] == False and i.keyDown[1] == False:
                i.velx = 0
                i.vely = 0
            if i.keyDown[2] == False and i.keyDown[3] == False:
                i.winkelnext = 0


            if i.x + self.ballsize / self.len > 1:
                i.x = 1 - self.ballsize / self.len
            if i.y + self.ballsize / self.len > 1:
                i.y = 1 - self.ballsize / self.len
            if i.x - self.ballsize / self.len < 0:
                i.x = self.ballsize / self.len
            if i.y - self.ballsize / self.len < 0:
                i.y = self.ballsize / self.len

            i.x += i.velx
            i.y += i.vely
            i.winkel += i.winkelnext


    def createWalls(self, ran):
        self.wallsbuild = True
        for i in range(4):
            for j in range(4):
                a = [(1 / 4) * j, (1 / 4) * i]
                self.wallscoordinates.append(a)
        if ran == 1:
            self.wallscoordinates[0].append(3)
            self.wallscoordinates[1].append(0)
            self.wallscoordinates[2].append(3)
            self.wallscoordinates[3].append(0)
            self.wallscoordinates[4].append(0)
            self.wallscoordinates[5].append(0)
            self.wallscoordinates[6].append(2)
            self.wallscoordinates[7].append(0)
            self.wallscoordinates[8].append(2)
            self.wallscoordinates[9].append(0)
            self.wallscoordinates[10].append(0)
            self.wallscoordinates[11].append(0)
            self.wallscoordinates[12].append(0)
            self.wallscoordinates[13].append(1)
            self.wallscoordinates[14].append(0)
            self.wallscoordinates[15].append(1)
        elif ran == 2:
            self.wallscoordinates[0].append(0)
            self.wallscoordinates[1].append(3)
            self.wallscoordinates[2].append(3)
            self.wallscoordinates[3].append(0)
            self.wallscoordinates[4].append(2)
            self.wallscoordinates[5].append(0)
            self.wallscoordinates[6].append(2)
            self.wallscoordinates[7].append(0)
            self.wallscoordinates[8].append(2)
            self.wallscoordinates[9].append(0)
            self.wallscoordinates[10].append(2)
            self.wallscoordinates[11].append(0)
            self.wallscoordinates[12].append(0)
            self.wallscoordinates[13].append(1)
            self.wallscoordinates[14].append(1)
            self.wallscoordinates[15].append(0)
        elif ran == 3:
            self.wallscoordinates[0].append(0)
            self.wallscoordinates[1].append(0)
            self.wallscoordinates[2].append(3)
            self.wallscoordinates[3].append(0)
            self.wallscoordinates[4].append(2)
            self.wallscoordinates[5].append(0)
            self.wallscoordinates[6].append(2)
            self.wallscoordinates[7].append(0)
            self.wallscoordinates[8].append(2)
            self.wallscoordinates[9].append(0)
            self.wallscoordinates[10].append(2)
            self.wallscoordinates[11].append(0)
            self.wallscoordinates[12].append(0)
            self.wallscoordinates[13].append(1)
            self.wallscoordinates[14].append(0)
            self.wallscoordinates[15].append(0)
        elif ran == 4:
            self.wallscoordinates[0].append(0)
            self.wallscoordinates[1].append(0)
            self.wallscoordinates[2].append(0)
            self.wallscoordinates[3].append(0)
            self.wallscoordinates[4].append(0)
            self.wallscoordinates[5].append(3)
            self.wallscoordinates[6].append(4)
            self.wallscoordinates[7].append(0)
            self.wallscoordinates[8].append(0)
            self.wallscoordinates[9].append(2)
            self.wallscoordinates[10].append(1)
            self.wallscoordinates[11].append(0)
            self.wallscoordinates[12].append(0)
            self.wallscoordinates[13].append(0)
            self.wallscoordinates[14].append(0)
            self.wallscoordinates[15].append(0)
        elif ran == 5:
            self.wallscoordinates[0].append(2)
            self.wallscoordinates[1].append(2)
            self.wallscoordinates[2].append(2)
            self.wallscoordinates[3].append(0)
            self.wallscoordinates[4].append(3)
            self.wallscoordinates[5].append(0)
            self.wallscoordinates[6].append(0)
            self.wallscoordinates[7].append(3)
            self.wallscoordinates[8].append(0)
            self.wallscoordinates[9].append(0)
            self.wallscoordinates[10].append(0)
            self.wallscoordinates[11].append(0)
            self.wallscoordinates[12].append(2)
            self.wallscoordinates[13].append(2)
            self.wallscoordinates[14].append(2)
            self.wallscoordinates[15].append(0)
        elif ran == 6:
            self.wallscoordinates[0].append(0)
            self.wallscoordinates[1].append(2)
            self.wallscoordinates[2].append(0)
            self.wallscoordinates[3].append(0)
            self.wallscoordinates[4].append(2)
            self.wallscoordinates[5].append(0)
            self.wallscoordinates[6].append(2)
            self.wallscoordinates[7].append(0)
            self.wallscoordinates[8].append(0)
            self.wallscoordinates[9].append(3)
            self.wallscoordinates[10].append(3)
            self.wallscoordinates[11].append(0)
            self.wallscoordinates[12].append(0)
            self.wallscoordinates[13].append(0)
            self.wallscoordinates[14].append(0)
            self.wallscoordinates[15].append(0)
        elif ran == 7:
            self.wallscoordinates[0].append(3)
            self.wallscoordinates[1].append(0)
            self.wallscoordinates[2].append(0)
            self.wallscoordinates[3].append(3)
            self.wallscoordinates[4].append(0)
            self.wallscoordinates[5].append(0)
            self.wallscoordinates[6].append(0)
            self.wallscoordinates[7].append(0)
            self.wallscoordinates[8].append(0)
            self.wallscoordinates[9].append(3)
            self.wallscoordinates[10].append(3)
            self.wallscoordinates[11].append(0)
            self.wallscoordinates[12].append(0)
            self.wallscoordinates[13].append(0)
            self.wallscoordinates[14].append(0)
            self.wallscoordinates[15].append(0)
        elif ran == 8:
            self.wallscoordinates[0].append(2)
            self.wallscoordinates[1].append(3)
            self.wallscoordinates[2].append(0)
            self.wallscoordinates[3].append(0)
            self.wallscoordinates[4].append(3)
            self.wallscoordinates[5].append(2)
            self.wallscoordinates[6].append(3)
            self.wallscoordinates[7].append(0)
            self.wallscoordinates[8].append(2)
            self.wallscoordinates[9].append(3)
            self.wallscoordinates[10].append(3)
            self.wallscoordinates[11].append(0)
            self.wallscoordinates[12].append(0)
            self.wallscoordinates[13].append(0)
            self.wallscoordinates[14].append(0)
            self.wallscoordinates[15].append(0)



        for i in range(16):
            if (self.wallscoordinates[i][2] != 0):
                self.walls.append(
                    Wall(self.wallscoordinates[i][0], self.wallscoordinates[i][1], self.wallscoordinates[i][2],
                         1, 1, self.ox, self.oy, self.len))

    def getbounceBallPlayer(self, ball, j):
        d = math.sqrt((ball.x - j.x) ** 2 + (ball.y - j.y) ** 2)
        if d < 17 / self.len:
            if ball.ID == 1:
                self.ballcount1 -= 1
                self.score2 += 1
            elif ball.ID == 2:
                self.ballcount2 -= 1
                self.score1 += 1
            self.balls.remove(ball)
            return True
        else:
            return False

    def getBoundeWallPlayer(self):

        for i in self.walls:
            for j in self.players:
                d = math.sqrt((i.points.x() - j.x) ** 2 + (i.points.y() - j.y) ** 2)
                e = math.sqrt((i.pointe.x() - j.x) ** 2 + (i.pointe.y() - j.y) ** 2)
                verticalwall = (i.points.x() * 100 == j.x * 100 // 1 + self.ballsize / self.len or
                                i.points.x() * 100 == j.x * 100 // 1 - self.ballsize / self.len) \
                               and i.points.y() <= j.y < i.pointe.y()
                horizontalwall = (i.points.y() * 100 == j.y * 100 // 1 + self.ballsize / self.len or
                                  i.points.y() * 100 == j.y * 100 // 1 - self.ballsize / self.len) \
                                 and i.points.x() <= j.x < i.pointe.x()
                if e < 15 / self.len or d < 15 / self.len or horizontalwall or verticalwall:
                    j.x = j.x - j.velx
                    j.y = j.y - j.vely

    def getBoundePlayer_Player(self):
        for i in range(len(self.players)):
            for j in range(len(self.players)):
                if i != j and i < j:
                    d = math.sqrt((self.players.x - self.players.x) ** 2 + (self.players.y - self.players.y) ** 2)
                    if d < 30 / self.len:
                        self.players.x = self.players.x - self.players.velx
                        self.players.y = self.players.y - self.players.vely


    def getBounceWall(self):
        for i in self.balls:
            for j in self.walls:
                if j.points.y() == i.getY() and j.points.x() == i.getX() or j.pointe.y() == i.getY() \
                        and j.pointe.x() == i.getX():
                    i.hitX()
                    i.hitY()
                elif j.getSeite() % 2 == 0 and j.points.x() == i.getX()//1 and j.points.y() <= i.getY() // 1 < j.pointe.y():
                    i.hitX()
                elif j.getSeite() % 2 == 1 and j.points.y() == i.getY()//1 and j.points.x() <= i.getX() // 1 < j.pointe.x():
                    i.hitY()


    def spawnBall(self,winkel, x , y, ID):
        if self.lebendig:
            self.balls.append(Ball(math.cos(winkel) * 5, math.sin(winkel) * 5,
                                   x + (math.cos(winkel) * 20),
                                   y + math.sin(winkel) * 20, 1, 1, ID))

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




    def paintEvent(self, e):

        if not self.lebendig:
            self.run = False
        if not self.run:
            self.balls = []
            self.walls = []
            self.wallsbuild = False
            self.wallscoordinates = []
            self.run = True
            self.lebendig = True
            self.winkel = 0
            self.players = []
            self.alive = False
            self.ballcount1 = 0
            self.ballcount2 = 0

        self.getBounceWall()
        #self.getBoundePlayer_Player()
        if not self.alive:
            for i in range(2):
                self.players.append(Player(i+1))
                self.alive = True

        if not self.wallsbuild:
            self.level_id = random.randint(1, 8)
            self.createWalls(self.level_id)

        self.playerMovment()

        self.getBoundeWallPlayer()
        painter = QPainter(self)

        for j in self.players:
            for i in self.balls:
                if self.getbounceBallPlayer(i, j):
                    self.lebendig = False

        for i in self.players:
            if i.alive:
                painter.setBrush(QColor(i.color))

                painter.drawEllipse(QPoint(self.ox + self.len * i.x,self.ox + self.len * i.y), self.ballsize, self.ballsize)
                painter.setBrush(QColor('green'))
                painter.drawLine(QPoint(self.ox + self.len * i.x,self.ox + self.len * i.y), QPoint(self.ox + self.len * i.x + (math.cos(i.winkel) * 20), self.ox + self.len * i.y + ((math.sin(i.winkel))) * 20))

        for i in self.balls:
            i.move()
            if i.getLife() <= 0:
                if i.ID == 1:
                    self.ballcount1 -= 1
                if i.ID == 2:
                    self.ballcount2 -= 1
                self.balls.remove(i)
            painter.setBrush(QColor('black'))
            self.point = QPoint(self.ox + self.len * i.getX(), self.ox + self.len * i.getY())
            painter.drawEllipse(self.point, 2, 2)

        for i in self.walls:
            painter.setBrush(QColor('black'))
            painter.drawLine(i.points, i.pointe)


        self.main.statusBar().clearMessage()
        self.main.statusBar().showMessage("Score Player1: " + str(self.score1) + "\t" +
                                          "Score Player2: " + str(self.score2) + " Server")







class MyMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(700, 100, 600, 600)

        self.renderarea = MyRenderArea(self)




        statusbar = self.statusBar()
        # Anzeigen eines Textes in der Statuszeile für eine Sekunde.
        statusbar.showMessage('Start')

        #renderarea = MyRenderArea(self)
        self.setCentralWidget(self.renderarea)

        self.show()
    def reset_func(self):
        self.renderarea.setRun(False)



app = QApplication([])
gui = MyMainWindow()
exit(app.exec_())
