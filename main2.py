import sys
import os
import unicodedata
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QFileDialog, QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, QEvent, QObject

class QLineEditDropHandler(QObject):

    def __init__(self, parent=None):
        QObject.__init__(self, parent)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.DragEnter:
            # we need to accept this event explicitly to be able to receive QDropEvents!
            event.accept()
        if event.type() == QEvent.Drop:
            md = event.mimeData()
            if md.hasUrls():
                for url in md.urls():
                    obj.setText(url.path())
                    break
            event.accept()
        return QObject.eventFilter(self, obj, event)


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'M3U Generator'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, 400, 120)
        self.setFixedSize(400, 120)
        self.setWindowIcon(QIcon.fromTheme("multimedia-playlist"))

        self.textbox = QLineEdit(self)
        self.textbox.move(10, 10)
        self.textbox.resize(380, 26)
        self.textbox.setReadOnly(True)
        self.textbox.installEventFilter(QLineEditDropHandler(self))

        self.selectbutton = QPushButton("Select Folder", self)
        self.selectbutton.clicked.connect(self.getDir)
        self.selectbutton.setIcon(QIcon.fromTheme("folder"))
        self.selectbutton.setStyleSheet("padding: 2px; padding-left: 2px;")
        self.selectbutton.resize(120, 26)
        self.selectbutton.move(10, 50)

        self.gobutton = QPushButton("create List", self)
        self.gobutton.clicked.connect(self.genM3U)
        self.gobutton.setIcon(QIcon.fromTheme("ok"))
        self.gobutton.setStyleSheet("padding: 2px; padding-left: 2px;")
        self.gobutton.resize(120, 26)
        self.gobutton.move(270, 50)
        self.statusBar().showMessage("Ready", 0)

        self.show()

    def dropEvent( self, event ):
        data = event.mimeData()
        urls = data.urls()
        if ( urls and urls[0].scheme() == 'file' ):
            # for some reason, this doubles up the intro slash
            filepath = str(urls[0].path())[1:]
            self.textbox.setText(filepath)

    def getDir(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.Directory)

        if dlg.exec_():
            files = dlg.selectedFiles()
            if len(files) < 1:
                return
            self.textbox.setText(dlg.selectedFiles()[0])

    def genM3U(self):
        selectDir = self.textbox.text()
        if not os.path.isdir(selectDir):
            return

        def isMusic(path):
            supportExtension = ['.mp3', '.m3u', '.wma', '.flac', '.wav', '.mc', '.aac', '.m4a', '.ape', '.dsf', '.dff']
            filename, fileExtension = os.path.splitext(path)
            if fileExtension.lower() in supportExtension:
                return True
            return False

        def createPlayList(selectDir):
            m3uList = []
            for root, subdirs, files in os.walk(selectDir):
                for filename in files:
                    relDir = os.path.relpath(root, selectDir)
                    if relDir == ".":
                        path = filename
                    else:
                        path = os.path.join(relDir, filename)
                    if isMusic(path):
                        m3uList.append(path)
            return m3uList

        m3uPath = os.path.join(selectDir, os.path.basename(selectDir) + ".m3u")

        if os.path.exists(m3uPath):
            os.remove(m3uPath)

        m3uList = createPlayList(selectDir)

        f = open(m3uPath, 'w', encoding='utf-8')
        for music in m3uList:
            f.write(unicodedata.normalize('NFC', music) + '\n')
        f.close()
        print("finished")
        self.statusBar().showMessage("%s%s%s" % ("Playlist '", os.path.basename(selectDir), "' created!"), 0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
