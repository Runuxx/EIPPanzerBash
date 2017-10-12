"""Game of Fabian Peters, Tim Heussler, Till Goebel, Taner Celik"""

from PyQt5.QtCore import Qt, QRect, QLine, QPoint, QTimer, QByteArray, QDataStream, QIODevice
from PyQt5.QtGui import QColor, QPainter, QPen, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMenu
from PyQt5.QtNetwork import QTcpServer, QHostAddress
import math, random
from PyQt5.QtNetwork import QTcpServer, QHostAddress, QTcpSocket

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


    def getStart(self):
        return self.points

    def getEnd(self):
        return self.pointe

    def getSeite(self):
        return self.seite



class Player():
    def __init__(self, ID):
        self.keyDown = [False,False,False,False,False]
        self.ID = ID
        self.velx = 0
        self.vely = 0
        self.winkel = 0
        self.winkelnext = 0
        self.alive = True
        if ID == 1:
            self.x = 0.1
            self.y = 0.1
            self.color = 'yellow'

        if ID == 2:
            self.x = 0.9
            self.y = 0.9
            self.color = 'blue'

    def position_player(self, raw_data):
        data = raw_data.split("#")
        self.x = float(data[2])
        self.y = float(data[3])
        self.winkel = float(data[4])



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

        self.level_id = 1
        self.wallscoordinates = []
        self.walls = []
        self.wallsbuild = False
        self.run = True

        #
        self.game_data = []

        # Die Membervariable tcpSocket verwaltet den Kommunikationskanal zum Server.
        self.tcpSocket = QTcpSocket(self)
        # In der connectToHost-Routine muss die IP-Adresse des Servers eingetragen werden.
        # Hier steht zurzeit nur die localhost Adresse: 127.0.0.1
        self.tcpSocket.connectToHost('127.0.0.1', 40890)
        self.tcpSocket.readyRead.connect(self.readData)

    def readData(self):
        instr = QDataStream(self.tcpSocket)
        raw_data = instr.readQString()

        if raw_data != "":
            self.writeData()
            self.update()
        data = raw_data.split("l")

        if self.level_id != int(data[1]):
            self.level_id = int(data[1])
            self.lebendig = False
            print("HI", self.wallsbuild)

        data_players = data[0].split("p")

        if len(data_players) > 1:
            del data_players[0]
            self.game_data = data_players

    def writeData(self):
        block = QByteArray()
        out = QDataStream(block, QIODevice.ReadWrite)

        controls = ""
        for b in self.players[1].keyDown:
            if b:
                controls += "1"
            else:
                controls += "0"
        if self.players[1].keyDown[4]:
            self.players[1].keyDown[4] = False
        print("OUT: ", controls)

        out.writeQString(controls)
        self.tcpSocket.write(block)

    def getRun(self):
        return self.run

    def setRun(self,run):
        self.run = run


    # Memberfunktion zur Handhabung von KeyPress-Events
    def keyPressEvent(self, e: QtGui.QKeyEvent):
        for i in self.players:

            if i.ID == 2:
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

    def position_players(self):
        index = 0
        for player in self.players:
            player.position_player(self.game_data[index])
            index += 1

    def keyReleaseEvent(self, e):
        for i in self.players:
            if i.ID == 2:
                if e.key() == Qt.Key_W:
                    i.keyDown[0] = False
                if e.key() == Qt.Key_S:
                    i.keyDown[1] = False
                if e.key() == Qt.Key_A:
                    i.keyDown[2] = False
                if e.key() == Qt.Key_D:
                    i.keyDown[3] = False
                if e.key() == Qt.Key_V:
                    i.keyDown[4] = False
            '''
            if i.ID == 2:
                if e.key() == Qt.Key_Up:
                    i.keyDown[0] = False
                if e.key() == Qt.Key_Down:
                    i.keyDown[1] = False
                if e.key() == Qt.Key_Left:
                    i.keyDown[2] = False
                if e.key() == Qt.Key_Right:
                    i.keyDown[3] = False
            '''

            if i.keyDown[0] == False and i.keyDown[1] == False:
                i.velx = 0
                i.vely = 0
            if i.keyDown[2] == False and i.keyDown[3] == False:
                i.winkelnext = 0

    def playerMovement(self):

        max_speed = 0.4

        if self.players[1].keyDown[0]:
            self.players[1].velx = (math.cos(self.players[1].winkel) * max_speed)
            self.players[1].vely = (math.sin(self.players[1].winkel) * max_speed)
        if self.players[1].keyDown[1]:
            self.players[1].velx = -(math.cos(self.players[1].winkel) * max_speed)
            self.players[1].vely = -(math.sin(self.players[1].winkel) * max_speed)
        if self.players[1].keyDown[2]:
            self.players[1].winkelnext = - 0.05
        if self.players[1].keyDown[3]:
            self.players[1].winkelnext = + 0.05


        if self.players[1].x + self.ballsize > self.width():
            self.players[1].x = self.width() - self.ballsize
        if self.players[1].y + self.ballsize > self.height():
            self.players[1].y = self.height() - self.ballsize
        if self.players[1].x - self.ballsize < 0:
            self.players[1].x = self.ballsize
        if self.players[1].y - self.ballsize < 0:
            self.players[1].y = self.ballsize

        self.players[1].x += self.players[1].velx
        self.players[1].y += self.players[1].vely
        self.players[1].winkel += self.players[1].winkelnext


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

            if self.wallscoordinates[i][2] != 0:

                self.walls.append(
                    Wall(self.wallscoordinates[i][0], self.wallscoordinates[i][1], self.wallscoordinates[i][2],
                         1, 1, self.ox, self.oy, self.len))

    def getbounceBallPlayer(self, ball, j):
        d = math.sqrt((ball.getX() - j.x) ** 2 + (ball.getY() - j.y) ** 2)
        if d < 17:
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
                verticalwall = (i.points.x() == j.x // 1 + self.ballsize or i.points.x() == j.x // 1 - self.ballsize) \
                               and i.points.y() <= j.y < i.pointe.y()
                horizontalwall = (i.points.y() == j.y // 1 + self.ballsize or i.points.y() == j.y // 1 - self.ballsize) \
                                 and i.points.x() <= j.x < i.pointe.x()
                if e < 15  or d < 15 or horizontalwall or verticalwall:
                    j.x = j.x - j.velx
                    j.y = j.y - j.vely

    def getBoundePlayer_Player(self):
        for i in range(len(self.players)):
            for j in range(len(self.players)):
                if i != j and i < j:
                    d = math.sqrt((self.players.x - self.players.x) ** 2 + (self.players.y - self.players.y) ** 2)
                    if d < 30:
                        self.players.x = self.players.x - self.players.velx
                        self.players.y = self.players.y - self.players.vely


    def getBounceWall(self):
        for i in self.balls:
            for j in self.walls:
                if j.points.y() == i.getY() and j.points.x() == i.getX() or j.pointe.y() == i.getY() and j.pointe.x() == i.getX():
                    i.hitX()
                    i.hitY()
                elif j.getSeite() % 2 == 0 and j.points.x() == i.getX()//1 and j.points.y() <= i.getY()//1 and j.pointe.y() > i.getY()//1:
                    i.hitX()
                elif j.getSeite() % 2 == 1 and j.points.y() == i.getY()//1 and j.points.x() <= i.getX()//1 and j.pointe.x() > i.getX()//1:
                    i.hitY()


    def spawnBall(self,winkel, x , y, ID):
        if self.lebendig:
            self.balls.append(Ball(math.cos(winkel) * 5, math.sin(winkel) * 5,
                                   x + (math.cos(winkel) * 20),
                                   y + math.sin(winkel) * 20, self.width(), self.height(), ID))

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

        self.tex_scale = self.len / self.background_tex.width()

    def paintEvent(self, e):
        self.position_players()
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



        self.getBoundeWallPlayer()
        painter = QPainter(self)

        for j in self.players:
            for i in self.balls:
                if self.getbounceBallPlayer(i, j):
                    self.lebendig = False



        for i in self.players:

            if i.alive:
                painter.setBrush(QColor(i.color))

                painter.drawEllipse(QPoint(self.ox + self.len * i.x, self.ox + self.len * i.y), self.ballsize, self.ballsize)
                painter.setBrush(QColor('green'))
                painter.drawLine(QPoint(self.ox + self.len * i.x, self.ox + self.len * i.y), QPoint(self.ox + self.len * i.x + (math.cos(i.winkel) * 20), self.ox + self.len * i.y + ((math.sin(i.winkel))) * 20))

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
                                          "Score Player2: " + str(self.score2) + " Client")







class MyMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(100, 100, 600, 600)

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
