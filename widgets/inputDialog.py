from qtpy.QtWidgets import QDialog, QFormLayout, QVBoxLayout, QLineEdit, QFrame, QPushButton, QHBoxLayout, QWidget
from qtpy.QtCore import Qt


class InputDialog(QDialog):
    def __init__(self, title, attributes_list, parent=None):
        """
        :param title: Title of the dialog
        :param attributes: Attributes of the dialog.
        Looks like
        [
            ('key1', 'value1', True),
            ('key2', 'value2', False),
            ...
        ]
        :param parent:
        """
        super().__init__(parent)
        self.__initVal(attributes_list)
        self.__initUi(title)

    def __initVal(self, attributes_list):
        self.__attr = attributes_list

    def __initUi(self, title):
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)

        self.__lay = QFormLayout()

        for obj in self.__attr:
            key, value, required = obj
            lineEdit = QLineEdit(value)
            self.__lay.addRow(key, lineEdit)
            lineEdit.textChanged.connect(self.__setAccept)

        mainWidget = QWidget()
        mainWidget.setLayout(self.__lay)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)

        self.__okBtn = QPushButton('OK')
        self.__okBtn.clicked.connect(self.accept)

        cancelBtn = QPushButton('Cancel')
        cancelBtn.clicked.connect(self.close)

        lay = QHBoxLayout()
        lay.addWidget(self.__okBtn)
        lay.addWidget(cancelBtn)
        lay.setAlignment(Qt.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        okCancelWidget = QWidget()
        okCancelWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(mainWidget)
        lay.addWidget(sep)
        lay.addWidget(okCancelWidget)

        self.setLayout(lay)

        self.__setAccept()

    def getAttributes(self):
        return [value.text() for value in [self.__lay.itemAt(i).widget() for i in range(self.__lay.count())]]

    def __setAccept(self):
        # Enable OK button if all required fields are filled
        # Get widgets in the form layout
        widgets = [self.__lay.itemAt(i).widget() for i in range(self.__lay.count())]
        for i, obj in enumerate(self.__attr):
            key, value, required = obj
            if required:
                if not widgets[i].text().strip():
                    self.__okBtn.setEnabled(False)
                    return
        self.__okBtn.setEnabled(True)