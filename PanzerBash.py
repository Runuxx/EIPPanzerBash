"""Game of Fabian Peters, Tim Heussler, Till Goebel, Taner Celik"""

from PyQt5.QtCore import Qt, QRect, QLine, QPoint
from PyQt5.QtGui import QColor, QPainter, QPen, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMenu
import math, random

from qtpy import QtGui


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
    def __init__(self, x, y, seite, height, width):
        self.width = width
        self.height = height
        self.seite = seite
        self.x = x
        self.y = y
        self.draw()

    def draw(self):
        if self.seite == 4:
            self.points = QPoint(self.x, self.y)
            self.pointe = QPoint(self.x, self.y + self.height / 4)
        if self.seite == 1:
            self.points = QPoint(self.x, self.y)
            self.pointe = QPoint(self.x + self.width / 4, self.y)
        if self.seite == 2:
            self.points = QPoint(self.x + self.width / 4, self.y)
            self.pointe = QPoint(self.x + self.width / 4, self.y + self.height / 4)
        if self.seite == 3:
            self.points = QPoint(self.x, self.y + self.height / 4)
            self.pointe = QPoint(self.x + self.width / 4, self.y + self.height / 4)


    def getStart(self):
        return self.points

    def getEnd(self):
        return self.pointe

    def getSeite(self):
        return self.seite

class Player():
    def __init__(self, ID):
        self.keyDown = [False,False,False,False]
        self.ID = ID
        self.velx = 0
        self.vely = 0
        self.winkel = 0
        self.winkelnext = 0
        self.alive = True
        if ID == 1:
            self.x = 100
            self.y = 100
            self.color = 'yellow'

        if ID == 2:
            self.x = 500
            self.y = 500
            self.winkel = math.pi
            self.color = 'blue'




class MyRenderArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Das Zeichenfeld muss den Focus für KeyPress-Events erhalten.
        self.setFocusPolicy(Qt.StrongFocus)
        # Wir laden eine png-Datei (mit Transparenz) und skalieren das Bild
        # auf die gewünschte Größe.
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

        self.wallscoordinates = []
        self.walls = []
        self.wallsbuild = False
        self.run = True


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
                    if self.ballcount1 < 6:
                        self.ballcount1 += 1
                        self.spawnBall(i.winkel, i.x, i.y, i.ID)
                    else: pass

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

            if i.keyDown[0] == False and i.keyDown[1] == False:
                i.velx = 0
                i.vely = 0
            if i.keyDown[2] == False and i.keyDown[3] == False:
                i.winkelnext = 0

    def playerMovement(self):
        for i in self.players:

            if i.keyDown[0]:
                i.velx = (math.cos(i.winkel) * 0.3)
                i.vely = (math.sin(i.winkel) * 0.3)
            if i.keyDown[1]:
                i.velx = -(math.cos(i.winkel) * 0.3)
                i.vely = -(math.sin(i.winkel) * 0.3)
            if i.keyDown[2]:
                i.winkelnext = - 0.01
            if i.keyDown[3]:
                i.winkelnext = + 0.01


            if i.x + self.ballsize > self.width():
                i.x = self.width() - self.ballsize
            if i.y + self.ballsize > self.height():
                i.y = self.height() - self.ballsize
            if i.x - self.ballsize < 0:
                i.x = self.ballsize
            if i.y - self.ballsize < 0:
                i.y = self.ballsize

            i.x += i.velx
            i.y += i.vely
            i.winkel += i.winkelnext


    def createWalls(self):
        self.wallsbuild = True
        for i in range(4):
            for j in range(4):
                a = [(self.width() // 4) * j, (self.height() // 4) * i]
                self.wallscoordinates.append(a)
        ran = random.randint(1, 8)
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
                         self.height(), self.width()))

    def getbounceBallPlayer(self, ball, j):
                d = math.sqrt((ball.getX() - j.x) ** 2 + (ball.getY() - j.y) ** 2)
                if d < 17:
                    if j.ID == 1:
                        self.ballcount1 -= 1
                        self.score2 += 1
                    elif j.ID == 2:
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
                    if e < 15 or d < 15 or horizontalwall or verticalwall:
                        j.x = j.x - j.velx
                        j.y = j.y - j.vely

    def getBoundePlayer_Player(self):
        for i in range(len(self.players)):
            for j in range(len(self.players)):
                if i != j and i < j:
                    d = math.sqrt((self.players[i].x - self.players[j].x) ** 2 + (self.players[i].y - self.players[j].y) ** 2)
                    if d < 30:
                        self.players[i].x = self.players[i].x - self.players[i].velx
                        self.players[i].y = self.players[i].y - self.players[i].vely
                        self.players[j].x = self.players[j].x - self.players[j].velx
                        self.players[j].y = self.players[j].y - self.players[j].vely

    def getBoundeWallBall(self):
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
            self.balls.append(Ball(math.cos(winkel) * 0.4, math.sin(winkel) * 0.4,
                               x + (math.cos(winkel) * 20),
                               y + math.sin(winkel) * 20, self.width(), self.height(), ID))


    def paintEvent(self, e):

        if not self.lebendig:
            self.run = False
        if not self.run:
            self.balls = []
            self.walls = []
            self.wallsbuild = False
            self.wallscoordinates = []
            self.x = 100
            self.y = 100
            self.run = True
            self.lebendig = True
            self.winkel = 0
            self.players = []
            self.alive = False
            self.ballcount1 = 0
            self.ballcount2 = 0

        self.getBoundeWallBall()

        if not self.alive:
            for i in range(2):
                self.players.append(Player(i+1))
                self.alive = True

        if not self.wallsbuild:
            self.createWalls()

        self.playerMovement()

        self.getBoundeWallPlayer()
        self.getBoundePlayer_Player()
        painter = QPainter(self)

        for j in self.players:
            for i in self.balls:
                if self.getbounceBallPlayer(i, j):
                    self.lebendig = False

        for i in self.players:
            if i.alive:
                painter.setBrush(QColor(i.color))

                painter.drawEllipse(QPoint(i.x,i.y), self.ballsize, self.ballsize)
                painter.setBrush(QColor('green'))
                painter.drawLine(QPoint(i.x,i.y), QPoint(i.x + (math.cos(i.winkel) * 20), i.y + ((math.sin(i.winkel))) * 20))

        for i in self.balls:
            i.move()
            if i.getLife() <= 0:
                if i.ID == 1:
                    self.ballcount1 -= 1
                if i.ID == 2:
                    self.ballcount2 -= 1
                self.balls.remove(i)
            painter.setBrush(QColor('black'))
            self.point = QPoint(i.getX(), i.getY())
            painter.drawEllipse(self.point, 2, 2)

        for i in self.walls:
            painter.setBrush(QColor('black'))
            painter.drawLine(i.getStart(), i.getEnd())


        self.main.statusBar().clearMessage()
        self.main.statusBar().showMessage("Score Player1: " + str(self.score1) + "\t" +
                                          "Score Player2: " + str(self.score2))


        self.update()





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
