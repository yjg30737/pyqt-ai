import os

from qtpy.QtCore import Signal, Qt
from qtpy.QtGui import QFontMetrics
from qtpy.QtWidgets import (
    QListWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QSpacerItem,
    QPushButton,
    QSizePolicy,
    QFileDialog,
    QFrame,
)


class DirListWidget(QWidget):
    itemUpdate = Signal(bool)
    onDirectorySelected = Signal(str)
    clicked = Signal(str)

    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__dirLblPrefix = "Directory: "
        self.__curDirName = ""

    def __initUi(self):
        lbl = QLabel("Files")
        setDirBtn = QPushButton("Set Directory")
        setDirBtn.clicked.connect(self.__setDir)
        self.__dirLbl = QLabel(self.__dirLblPrefix)

        lay = QHBoxLayout()
        lay.addWidget(lbl)
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(setDirBtn)
        lay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        self.__listWidget = QListWidget()
        self.__listWidget.itemClicked.connect(self.__sendDir)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(sep)
        lay.addWidget(self.__dirLbl)
        lay.addWidget(self.__listWidget)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)

    def __setDir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        ext_lst = [".txt", ".pdf"]
        if directory:
            self.__listWidget.clear()
            filenames = list(
                filter(
                    lambda x: os.path.splitext(x)[-1] in ext_lst, os.listdir(directory)
                )
            )
            self.__listWidget.addItems(filenames)
            self.itemUpdate.emit(len(filenames) > 0)
            self.__curDirName = directory
            self.__dirLbl.setText(self.__curDirName.split("/")[-1])

            self.__listWidget.setCurrentRow(0)
            # activate event as clicking first item (because this selects the first item anyway)
            if self.__listWidget.count() > 0:
                self.clicked.emit(
                    os.path.join(
                        self.__curDirName, self.__listWidget.currentItem().text()
                    )
                )
            self.onDirectorySelected.emit(self.__curDirName)

    def getDir(self):
        return self.__curDirName

    def __sendDir(self, item):
        self.clicked.emit(os.path.join(self.__curDirName, item.text()))
