import requests

from qtpy.QtCore import Signal
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QPushButton, QWidget, QHBoxLayout, QLineEdit, QLabel


class ApiWidget(QWidget):
    apiKeyAccepted = Signal(str, bool)

    def __init__(
        self,
        api_key: str = "",
        wrapper=None,
        settings=None,
        api_key_name="API_KEY",
        not_check_api=False,
        group_to_include=None,
    ):
        super().__init__()
        self.__initVal(
            api_key, wrapper, settings, api_key_name, not_check_api, group_to_include
        )
        self.__initUi()

    def __initVal(
        self,
        api_key: str = "",
        wrapper=None,
        settings=None,
        api_key_name="API_KEY",
        not_check_api=False,
        group_to_include=None,
    ):
        self.__api_key = api_key
        self.__wrapper = wrapper
        self.__settings_ini = settings
        self.__api_key_name = api_key_name

        self.__not_check_api = not_check_api
        self.__group_to_include = group_to_include

    def __initUi(self):
        self.__apiLineEdit = QLineEdit()
        self.__apiLineEdit.setEchoMode(QLineEdit.Password)
        self.__apiLineEdit.setText(self.__api_key)

        submitBtn = QPushButton("Submit")
        submitBtn.clicked.connect(self.setApi)

        self.__apiCheckPreviewLbl = QLabel()
        self.__apiCheckPreviewLbl.setVisible(False)

        lay = QHBoxLayout()
        lay.addWidget(QLabel("API KEY"))
        lay.addWidget(self.__apiLineEdit)
        lay.addWidget(submitBtn)
        lay.addWidget(self.__apiCheckPreviewLbl)

        self.setLayout(lay)

        self.setApi()

    def notCheckApi(self):
        self.__apiCheckPreviewLbl.hide()
        self.__not_check_api = True

    def setApi(self):
        f = False
        self.__api_key = self.__apiLineEdit.text()
        if self.__settings_ini:
            if self.__group_to_include:
                self.__settings_ini.beginGroup(self.__group_to_include)
            self.__settings_ini.setValue(self.__api_key_name, self.__api_key)
            if self.__group_to_include:
                self.__settings_ini.endGroup()
            if self.__not_check_api:
                self.__wrapper.request_and_set_api(self.__api_key)
                # This has to be set to True because we are not checking the API key
                f = True
            else:
                try:
                    f = self.__wrapper.request_and_set_api(self.__api_key)
                    if f:
                        self.__apiCheckPreviewLbl.setStyleSheet(
                            "color: {}".format(QColor(0, 200, 0).name())
                        )
                        self.__apiCheckPreviewLbl.setText("API key is valid")
                    else:
                        raise Exception
                except Exception as e:
                    self.__apiCheckPreviewLbl.setStyleSheet(
                        "color: {}".format(QColor(255, 0, 0).name())
                    )
                    self.__apiCheckPreviewLbl.setText("API key is invalid")
                finally:
                    self.__apiCheckPreviewLbl.show()
            self.apiKeyAccepted.emit(self.__api_key, f)
        else:
            self.apiKeyAccepted.emit(self.__api_key, f)

    def getApi(self):
        return self.__apiLineEdit.text()
