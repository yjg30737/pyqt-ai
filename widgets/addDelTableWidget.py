from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QVBoxLayout, QWidget, QTableWidget, \
    QLabel, QSizePolicy, QSpacerItem, QHBoxLayout, QPushButton, QTableWidgetItem, QDialog, QFormLayout

from widgets.inputDialog import InputDialog
from widgets.tableWidget import TableWidget


class AddDelTableWidget(QWidget):
    added = Signal(dict)

    def __init__(self, lbl, columns):
        super().__init__()
        self.__initVal(columns)
        self.__initUi(lbl)

    def __initVal(self, columns):
        self.__columns = columns

    def __initUi(self, lbl):
        columns = [obj['name'] for obj in self.__columns]

        self.__tableWidget = TableWidget(columns=columns)

        self.__addRowBtn = QPushButton('Add')
        self.__delRowBtn = QPushButton('Delete')

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
        lay.addWidget(self.__tableWidget)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

    def getTableWidget(self):
        return self.__tableWidget

    def __add(self):
        dialog = InputDialog('Add', self.__columns, self)
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            obj = dialog.getAttribute()
            self.addRecord(obj)
            self.added.emit(obj)

    def addRecord(self, obj):
        self.__tableWidget.addRecord(obj)

    def __delete(self):
        try:
            self.__tableWidget.removeRow(self.__tableWidget.currentRow())
        except Exception as e:
            print(e)