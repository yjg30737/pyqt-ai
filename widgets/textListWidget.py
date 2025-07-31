from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QListWidget,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QHBoxLayout,
    QPushButton,
    QDialog,
)

from inputDialog import InputDialog


class AddDelListWidget(QWidget):
    def __init__(self, lbl):
        super().__init__()
        self.__initUi(lbl)

    def __initUi(self, lbl):
        self.__listWidget = QListWidget()

        self.__addRowBtn = QPushButton("Add")
        self.__delRowBtn = QPushButton("Delete")

        self.__addRowBtn.clicked.connect(self.__add)
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
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

    def getListWidget(self):
        return self.__listWidget

    def __add(self):
        dialog = InputDialog("Add", [("Name", "", True)], self)
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            text = dialog.getText()
            self.__listWidget.addItem(text)

    def __delete(self):
        try:
            self.__listWidget.takeItem(
                self.__listWidget.row(self.__listWidget.currentItem())
            )
        except Exception as e:
            print(e)
