import os
from pathlib import Path

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QVBoxLayout, QWidget, QListWidget, \
    QLabel, QSizePolicy, QSpacerItem, QHBoxLayout, QPushButton, QDialog, QFileDialog

from widgets.imageView import ImageView


class FileListWidget(QWidget):
    def __init__(self, lbl):
        super().__init__()
        self.__initVal()
        self.__initUi(lbl)

    def __initVal(self):
        self.__extensions = ['.jpg', '.png']

    def __initUi(self, lbl):
        self.__listWidget = QListWidget()
        self.__listWidget.doubleClicked.connect(self.__showImage)

        self.__addRowBtn = QPushButton('Add')
        self.__delRowBtn = QPushButton('Delete')

        self.__addRowBtn.clicked.connect(self.__readingFiles)
        self.__delRowBtn.clicked.connect(self.__delete)

        lay = QHBoxLayout()
        lay.addWidget(QLabel(lbl))
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(self.__addRowBtn)
        lay.addWidget(self.__delRowBtn)
        lay.setAlignment(Qt.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        menuWidget = QWidget()
        menuWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(menuWidget)
        lay.addWidget(self.__listWidget)

        self.setLayout(lay)

        self.__toggle()
        self.setAcceptDrops(True)

    def __toggle(self):
        f = self.__listWidget.count() > 0
        self.__delRowBtn.setEnabled(f)

    def getListWidget(self):
        return self.__listWidget

    def __delete(self):
        try:
            self.__listWidget.takeItem(self.__listWidget.row(self.__listWidget.currentItem()))
            self.__toggle()
        except Exception as e:
            print(e)

    def __showImage(self):
        self.__imageView = ImageView()
        self.__imageView.setWindowModality(Qt.ApplicationModal)
        self.__imageView.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.__imageView.setWindowFlag(Qt.WindowCloseButtonHint)
        self.__imageView.setWindowTitle('View Image')
        self.__imageView.setFilename(self.__listWidget.currentItem().text())
        self.__imageView.show()

    def __readingFiles(self):
        filenames = QFileDialog.getOpenFileNames(self, 'Find', os.path.expanduser('~'),
                                                 'Image Files (*.jpg, *.png)')
        if filenames[0]:
            filenames = filenames[0]
            cur_file_extension = Path(filenames[0]).suffix

            if cur_file_extension in self.__extensions:
                self.__listWidget.addItems(filenames)

        self.__toggle()

    def __getExtFilteredFiles(self, lst):
        if len(self.__extensions) > 0:
            return list(filter(None, map(lambda x: x if os.path.splitext(x)[-1] in self.__extensions else None, lst)))
        else:
            return lst

    def __getUrlsFilenames(self, urls):
        return list(map(lambda x: x.path()[1:], urls))

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()

    def dragMoveEvent(self, e):
        pass

    def dropEvent(self, e):
        filenames = [file for file in self.__getExtFilteredFiles(
            self.__getUrlsFilenames(e.mimeData().urls())) if file]
        self.__listWidget.addItems(filenames)
        super().dropEvent(e)