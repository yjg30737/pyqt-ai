from qtpy.QtCore import Qt, Signal, QThread
from qtpy.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QHBoxLayout,
    QPushButton,
    QDialog,
)

from widgets.checkBoxTableWidget import CheckBoxTableWidget
from widgets.downloadDialog import DownloadDialog
from widgets.inputDialog import InputDialog
from widgets.tableWidget import TableWidget


class RemoveModelThread(QThread):
    def __init__(self, wrapper, models):
        super().__init__()
        self.__wrapper = wrapper
        self.__models = models

    def run(self):
        try:
            for model in self.__models:
                if self.__wrapper.model_exists(model):
                    self.__wrapper.remove_model(model)
                else:
                    print(f"Model {model} does not exist.")
        except Exception as e:
            print(f"Error: {e}")


class AddDelTableWidget(QWidget):
    added = Signal(dict)

    def __init__(self, lbl, columns, checkable=False, is_download=False, wrapper=None):
        super().__init__()
        self.__initVal(columns, is_download, checkable, wrapper)
        self.__initUi(lbl)

    def __initVal(self, columns, is_download=False, checkable=False, wrapper=None):
        self.__columns = columns
        self.__is_download = is_download
        self.__checkable = checkable
        self.__wrapper = wrapper

    def __initUi(self, lbl):
        columns = [obj["name"] for obj in self.__columns]

        self.__tableWidget = (
            TableWidget(columns=columns)
            if not self.__checkable
            else CheckBoxTableWidget(columns=columns)
        )

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
        lay.addWidget(self.__tableWidget)
        lay.setContentsMargins(0, 0, 0, 0)

        self.setLayout(lay)

        if self.__checkable:
            self.__tableWidget.checkedSignal.connect(self.__deleteButtonToggle)
            self.__delRowBtn.setEnabled(False)  # Initially disable delete button

    def getTableWidget(self):
        return self.__tableWidget

    def __add(self):
        if self.__is_download:
            dialog = DownloadDialog("Add", self.__columns, self)
        else:
            dialog = InputDialog("Add", self.__columns, self)

        reply = dialog.exec()
        if reply == QDialog.Accepted:
            if self.__is_download:
                model_name = dialog.getModelName()
                obj = {col["name"]: model_name for col in self.__columns}
            else:
                obj = dialog.getAttribute()
                self.addRecord(obj)
            self.added.emit(obj)

    def addRecord(self, obj):
        self.__tableWidget.addRecord(obj)

    def __delete(self):
        try:
            if self.__checkable:
                if self.__is_download:
                    self.__t = RemoveModelThread(
                        self.__wrapper,
                        # Get the model names
                        [
                            self.__tableWidget.item(i, 1).text()
                            for i in self.__tableWidget.getCheckedRows()
                        ],
                    )
                    self.__t.start()
                    self.__t.finished.connect(self.__tableWidget.removeCheckedRows)
            else:
                self.__tableWidget.removeRow(self.__tableWidget.currentRow())
        except Exception as e:
            print(e)

    def __deleteButtonToggle(self, r_idx, flag):
        if flag == Qt.Checked:
            self.__delRowBtn.setEnabled(True)
        else:
            if not self.__tableWidget.getCheckedRows():
                self.__delRowBtn.setEnabled(False)
