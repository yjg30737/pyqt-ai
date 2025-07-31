import os
import sys

# Get the absolute path of the current script file

script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

from qtpy.QtWidgets import (
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QMainWindow,
    QPushButton,
    QApplication,
    QGroupBox,
    QPlainTextEdit,
    QFormLayout,
    QSplitter,
    QComboBox,
    QSizePolicy,
)
from qtpy.QtCore import QSettings, Signal, QThread, Qt
from qtpy.QtGui import QFont, QIcon

from constants import ROOT_DIR
from widgets.apiWidget import ApiWidget
from widgets.imageView import ImageView
from scripts.openai_script import GPTGeneralWrapper

QApplication.setFont(QFont("Arial", 12))


class Thread(QThread):
    afterGenerated = Signal(str)
    errorGenerated = Signal(str)

    def __init__(self, wrapper, model, input_args):
        super().__init__()
        self.__wrapper = wrapper
        self.__model = model
        self.__input_args = input_args

    def run(self):
        try:
            image = self.__wrapper.get_image_response(
                model=self.__model, input_args=self.__input_args
            )
            self.afterGenerated.emit(image)
        except Exception as e:
            self.errorGenerated.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settings_ini = QSettings(
            os.path.join(ROOT_DIR, "settings.ini"), QSettings.IniFormat
        )
        if not self.__settings_ini.contains("API_KEY"):
            self.__settings_ini.setValue("API_KEY", "")
            self.__settings_ini.setValue("model", "dall-e-3")
            self.__settings_ini.setValue("width", 1024)
            self.__settings_ini.setValue("height", 1024)
            self.__settings_ini.setValue(
                "prompt",
                "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k",
            )
        self.__api_key = self.__settings_ini.value("API_KEY", type=str)
        self.__model = self.__settings_ini.value("model", type=str)
        self.__width = self.__settings_ini.value("width", type=int)
        self.__height = self.__settings_ini.value("height", type=int)
        self.__prompt = self.__settings_ini.value("prompt", type=str)
        self.__wrapper = GPTGeneralWrapper(self.__api_key)

    def __initUi(self):
        self.setWindowTitle("PyQt GPT DALL-E Example")

        self.__apiWidget = ApiWidget(
            self.__api_key, self.__wrapper, self.__settings_ini
        )
        self.__apiWidget.apiKeyAccepted.connect(self.__api_key_accepted)
        self.__imageWidget = ImageView()

        self.__promptWidget = QLineEdit()
        self.__promptWidget.setPlaceholderText("Enter the prompt...")

        self.__btn = QPushButton("Run")
        self.__btn.clicked.connect(self.__run)

        self.__widthComboBox = QComboBox()
        self.__widthComboBox.addItems(["256", "512", "1024", "1792"])
        self.__widthComboBox.setCurrentText(str(self.__width))
        self.__widthComboBox.currentTextChanged.connect(self.__attrChanged)

        self.__heightComboBox = QComboBox()
        self.__heightComboBox.addItems(["256", "512", "1024", "1792"])
        self.__heightComboBox.setCurrentText(str(self.__height))
        self.__heightComboBox.currentTextChanged.connect(self.__attrChanged)

        self.__promptWidget = QPlainTextEdit()
        self.__promptWidget.setPlainText(self.__prompt)
        self.__promptWidget.textChanged.connect(self.__attrChanged)

        self.__promptWidget.setMaximumHeight(100)

        lay = QFormLayout()
        lay.addRow("Width", self.__widthComboBox)
        lay.addRow("Height", self.__heightComboBox)
        lay.addRow("Prompt", self.__promptWidget)
        lay.setAlignment(Qt.AlignTop)

        optionGrpBox = QGroupBox("Settings")
        optionGrpBox.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(self.__apiWidget)
        lay.addWidget(self.__btn)
        lay.addWidget(self.__imageWidget)

        rightWidget = QWidget()
        rightWidget.setLayout(lay)

        splitter = QSplitter()
        splitter.addWidget(optionGrpBox)
        splitter.addWidget(rightWidget)
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)
        splitter.setSizes([500, 500])
        splitter.setStyleSheet("QSplitterHandle {background-color: lightgray;}")
        splitter.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding
        )

        self.setCentralWidget(splitter)

        self.__setAiEnabled(self.__wrapper.is_available())

    def __run(self):
        input_args = {
            "width": self.__width,
            "height": self.__height,
            "prompt": self.__prompt,
        }

        self.__t = Thread(self.__wrapper, self.__model, input_args)
        self.__t.started.connect(self.__started)
        self.__t.afterGenerated.connect(self.__afterGenerated)
        self.__t.finished.connect(self.__finished)
        self.__t.start()

    def __attrChanged(self, v):
        sender = self.sender()
        if sender == self.__widthComboBox:
            self.__width = int(v)
            self.__settings_ini.setValue("width", self.__width)
        elif sender == self.__heightComboBox:
            self.__height = int(v)
            self.__settings_ini.setValue("height", self.__height)
        elif sender == self.__promptWidget:
            self.__prompt = v
            self.__settings_ini.setValue("prompt", self.__prompt)

    def __api_key_accepted(self, api_key, f):
        # Enable AI related features if API key is valid
        self.__setAiEnabled(f)

    def __setAiEnabled(self, f):
        self.__btn.setEnabled(f)

    def __started(self):
        self.__btn.setEnabled(False)

    def __afterGenerated(self, data):
        self.__imageWidget.setBJson(data)

    def __finished(self):
        self.__btn.setEnabled(True)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    QApplication.setWindowIcon(QIcon("logo.png"))
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
