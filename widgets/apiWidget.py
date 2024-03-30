import requests

from qtpy.QtCore import Signal
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QPushButton, QWidget, QHBoxLayout, QLineEdit, QLabel


class ApiWidget(QWidget):
    apiKeyAccepted = Signal()

    def __init__(self, api_key: str = '', wrapper=None):
        super().__init__()
        self.__initVal(api_key, wrapper)
        self.__initUi()

    def __initVal(self, api_key: str, wrapper=None):
        self.__api_key = api_key
        self.__wrapper = wrapper

    def __initUi(self):
        self.__apiLineEdit = QLineEdit()
        self.__apiLineEdit.setEchoMode(QLineEdit.Password)
        self.__apiLineEdit.setText(self.__api_key)

        submitBtn = QPushButton('Submit')
        submitBtn.clicked.connect(self.apiKeyAccepted)

        self.__apiCheckPreviewLbl = QLabel()
        self.__apiCheckPreviewLbl.setVisible(False)

        lay = QHBoxLayout()
        lay.addWidget(QLabel('API KEY'))
        lay.addWidget(self.__apiLineEdit)
        lay.addWidget(submitBtn)
        lay.addWidget(self.__apiCheckPreviewLbl)

        self.setLayout(lay)

    def setApi(self, f):
        try:
            if f:
                self.__apiCheckPreviewLbl.setStyleSheet("color: {}".format(QColor(0, 200, 0).name()))
                self.__apiCheckPreviewLbl.setText('API key is valid')
            else:
                raise Exception
        except Exception as e:
            self.__apiCheckPreviewLbl.setStyleSheet("color: {}".format(QColor(255, 0, 0).name()))
            self.__apiCheckPreviewLbl.setText('API key is invalid')
            print(e)
        finally:
            self.__apiCheckPreviewLbl.show()

    def getApi(self):
        return self.__apiLineEdit.text()