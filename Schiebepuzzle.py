import os, sys, math
from random import randint

from PyQt5.QtCore import Qt, QRect, QLine
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QMenu, QWidget, QMessageBox


# Die Klasse MyRenderArea dient als Zeichenfläche. Sie ist von einem QWidget abgeleitet und
# erbt damit alle Membervariablen und -funktionen von dieser vordefinierten Klasse.
class MyRenderArea(QWidget):
    # Der Konstruktor, parent verweist auf das Widget, in das dieses Widget eingebettet wird.
    def __init__(self, parent=None):
        # Aufruf des Konstruktors der Oberklasse QWidget
        super().__init__(parent)
        # Wir merken uns das Parent-Widget
        self.main = parent
        # Wir erzeugen eine zufällige Permutation für die 16 Puzzle-Teile.
        # Der Wert 15 kodiert das leere Feld.
        r = [i for i in range(16)]
        for i in range(15, 0, -1):
            j = randint(0, i)
            r[j], r[i] = r[i], r[j]

        # Wir ordnen die Puzzle-Teile Zeile für Zeile an.
        self.feld = [[r[4 * i + j] for j in range(4)] for i in range(4)]
        # (mi,mj) kodiert die mi-te Zeile und mj-te Spalte des Puzzles, in der sich der Mauszeiger
        # befindet. (tx,ty) steht für die horizontale/vertikale Verschiebung des Mauszeigers seit
        # dem letzten Drücken einer Maustaste.
        self.mi = self.mj = self.tx = self.ty = 0

    # Wir überschreiben die Memberfunktion von QWidget, die auf Mausbewegungen mit einer gedrückten
    # Maustaste reagiert.
    def mouseMoveEvent(self, e):
        # Wir berechnen den Verschiebungsvektor (tx,ty) seit dem letzten Drücken einer Maustaste am
        # Ort (mx,my). Die aktuelle Mausposition kann aus dem Event e in Form (e.x(),e.y()) ausgelesen
        # werden.
        self.tx = e.x() - self.mx
        self.ty = e.y() - self.my
        # Wenn die Bewegung über die Länge eines Puzzle-Teils hinausgeht, wird sie beschränkt.
        if self.tx > self.len:
            self.tx = self.len
        if self.tx < -self.len:
            self.tx = -self.len
        if self.ty > self.len:
            self.ty = self.len
        if self.ty < -self.len:
            self.ty = -self.len
        # Anzeigen der Mausbewegung in der Statuszeile zu Debugging Zwecken.
        self.main.statusBar().showMessage("Maus−Move  (" + str(e.x()) + "," + str(e.y()) + ")", 4000)
        # Aktualisieren des Fensterinhaltes. update ruft die paintEvent-Funktion auf.
        self.update()

    # Überschreiben der Memberfunktion zur Behandlung von Maus-Press Events.
    def mousePressEvent(self, e):
        # Wir merken uns die Position (mx,my), an der eine Maustaste gedrückt wurde.
        self.mx = e.x()
        self.my = e.y()
        # Verschiebungsvektor zunächst mit (0,0) initialisieren.
        self.tx = 0
        self.ty = 0
        # Berechnung der (Zeile,Spalte)=(mi,mj) des selektierten Puzzle-Teils.
        self.mi = math.floor((e.y() - self.oy) / self.len)
        self.mj = math.floor((e.x() - self.ox) / self.len)
        # Kontrollausgabe in der Statuszeile
        self.main.statusBar().showMessage("Maus−Press (" + str(e.x()) + "," + str(e.y()) + ")", 4000)

    # Überschreiben des Maus-Release Events.
    def mouseReleaseEvent(self, e):
        # (Zeile,Spalte) des selektiertn Puzzle-Teils.
        i, j = self.mi, self.mj

        # Wenn die durchgeführte Bewegung zulässig war, aktualisieren wir die Beschriftung der
        # betroffenen Puzzle-Teile.
        # Bewegung nach rechts
        if self.tx == self.len and self.feld[i][j + 1] == 15:
            self.feld[i][j], self.feld[i][j + 1] = self.feld[i][j + 1], self.feld[i][j]
        # Bewegung nach links
        if self.tx == -self.len and self.feld[i][j - 1] == 15:
            self.feld[i][j], self.feld[i][j - 1] = self.feld[i][j - 1], self.feld[i][j]
        # Bewegung nach unten
        if self.ty == self.len and self.feld[i + 1][j] == 15:
            self.feld[i][j], self.feld[i + 1][j] = self.feld[i + 1][j], self.feld[i][j]
        # Bewegung nach oben
        if self.ty == -self.len and self.feld[i - 1][j] == 15:
            self.feld[i][j], self.feld[i - 1][j] = self.feld[i - 1][j], self.feld[i][j]

        # Kontrollausgabe in der Statuszeile
        self.main.statusBar().showMessage("Maus−Release (" + str(e.x()) + "," + str(e.y()) + ")", 4000)
        # Aktualisierung des Fensterinhaltes
        self.update()

    # Überschreiben der Methode zur Behandlung von Resize Events
    def resizeEvent(self, e):
        # (ox,oy) steht für die linke obere Ecke des quadratischen Spielfeldes und dient als
        # Ursprung des Koordinatensystems.
        if self.width() > self.height():
            self.len = self.height() / 4
            self.ox = (self.width() - self.height()) / 2
            self.oy = 0
        else:
            self.len = self.width() / 4
            self.ox = 0
            self.oy = (self.height() - self.width()) / 2

    # Überschreiben der Methode zum Bildaufbau
    def paintEvent(self, e):
        # Mit Hilfe des painters kann der Kontur- und Füllfarbe, Textfont, etc. gesetzt werden.
        painter = QPainter(self)
        # Setzen der Füllfarbe für den Hintergrund
        painter.setBrush(QColor('white'))
        # painter.setBrush(Qt.NoBrush)
        # keine Konturfarbe
        painter.setPen(Qt.NoPen)
        # Rechteck zum Löschen des Hintergrundes
        rect = QRect(0, 0, self.width(), self.height())
        # Zeichen den Hintergrundrechteckes
        painter.drawRect(rect)
        # Aktivieren von Antialiasing zur Vermeidung von Treppeneffekten
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Auswahl des Textfonts, angepasst auf die Länge eines Puzzle-Teils
        font = QFont('Times New Roman', 0.3 * self.len)
        # Setzen des Fonts im Painter
        painter.setFont(font)

        # Setzen der Füllfarbe für ein Puzzle-Teil
        painter.setBrush(QColor('light gray'))

        # Zeichnen aller 16 Puzzle-Teile
        for i in range(4):
            for j in range(4):
                # Das Puzzle-Teil mit dem Wert 15 entspricht dem leeren Feld.
                if self.feld[i][j] == 15:
                    continue

                # Bestimmung der linken oberen Ecke des Puzzle-Teils in Zeile i und Spalte j.
                px = self.ox + (j + 0.025) * self.len
                py = self.oy + (i + 0.025) * self.len

                # Beachtung des Verschiebungsvektors für das bewegte Puzzle-Teil.
                if i == self.mi and j == self.mj:
                    if abs(self.tx) > abs(self.ty):
                        if self.tx < 0 and j > 0 and self.feld[i][j - 1] == 15 or self.tx > 0 and j < 3 and \
                                        self.feld[i][j + 1] == 15:
                            px += self.tx
                    else:
                        if self.ty < 0 and i > 0 and self.feld[i - 1][j] == 15 or self.ty > 0 and i < 3 and \
                                        self.feld[i + 1][j] == 15:
                            py += self.ty

                # Erzeugen eines Rechtecks für das betrachtete Puzzle-Teil.
                rect = QRect(px, py, 0.95 * self.len, 0.95 * self.len)

                # Kontur-Farbe
                pen = QPen(QColor('black'))
                painter.setPen(pen)
                # Zeichnen des Puzzle-Rechtecks
                painter.drawRect(rect)
                # Font-Farbe
                pen = QPen(QColor('blue'))
                painter.setPen(pen)
                # Zeichnen der Ziffern des Puzzle-Teils
                painter.drawText(rect, Qt.AlignCenter, str(self.feld[i][j] + 1))


# Die Klasse MyMainWindow erbt alle Eigenschaften und Methoden der vordefinierten Klasse QMainWindow.
# Ein QMainWindow besteht im Allgemeinen aus einer Menüleiste am oberen Rand des Fensters und einer
# Statuszeile am unteren Rand des Fensters. In den zentralen Bereich setzen wir unsere Zeichenfläche.
class MyMainWindow(QMainWindow):
    def __init__(self):
        # Aufruf des Konstruktors für die Oberklasse QMainWindow
        super().__init__()
        # Festlegung der linken oberen Ecke (100,100) des Fensters in Bildschirmkoordinaten.
        # Festerbreite und -höhe betragen 600 x 600 Pixel.
        self.setGeometry(100, 100, 600, 600)

        # Erzeugung einer Menüleiste.
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        # Die Menüleiste enhält zwei Pulldown-Menüs: File + View
        fileMenu = menubar.addMenu('&File')
        # Das Pulldown-Menü 'File' besteht nur aus einem 'Exit' Eintrag. Wenn dieser
        # ausgewählt wird, wird die Anwendung verlassen (durch Aufruf der Memberfunktion close).
        fileMenu.addAction('Exit', self.close)
        # Das Pulldown-Menü 'View' besteht aus zwei Einträgen: 'Save' und 'About'.
        viewMenu = menubar.addMenu("&View")
        # Untermenü-Eintrag 'Save'. Bei Aktivierung wird die Memberfunktion saveTest aufgerufen.
        viewMenu.addAction('Save', lambda: self.saveTest())
        # Untermenü-Entrag 'About'. Bei Aktivierung wird eine MessageBox geöffnet.
        viewMenu.addAction('About Qt 5', lambda: QMessageBox.aboutQt(self))

        # Anlegen einer eigenen Zeichenfläche als zentrales Widget des QMainWindow.
        # Aufruf des Konstruktors für die von QWidget abgeleitete eigene Klasse MyRenderArea.
        renderarea = MyRenderArea(self)
        self.setCentralWidget(renderarea)

        # Anlegen einer Statuszeile am unteren Rand des QMainWindow.
        statusbar = self.statusBar()
        # Anzeigen eines Textes in der Statuszeile für eine Sekunde.
        statusbar.showMessage('Start', 1000)

        # Anzeigen des QMainWindow.
        self.show()

    #
    def saveTest(self):
        s = QFileDialog.getSaveFileName(self, "Save", os.path.expanduser("~"), "(*.puz) SchiebePUZzle", "puz")
        self.statusBar().showMessage('Save' + s[0], 10000)


# Hauptprogramm
# Anlegen der Applikation
app = QApplication([])
# Anlegen des eigenen MainWindows
gui = MyMainWindow()
# Eintritt in die Qt-Event-Schleife
exit(app.exec_())
