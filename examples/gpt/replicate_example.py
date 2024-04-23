import os
import sys

# Get the absolute path of the current script file

script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

from qtpy.QtWidgets import QLineEdit, QVBoxLayout, QFormLayout, QScrollArea, \
    QSplitter, QGroupBox, QComboBox, QSpinBox, QSizePolicy, QTextEdit, QMessageBox, QWidget, QMainWindow, QPushButton, QApplication
from qtpy.QtCore import QSettings, Signal, QThread, Qt
from qtpy.QtGui import QFont, QIcon

from settings import ROOT_DIR
from widgets.apiWidget import ApiWidget
from widgets.imageView import ImageView
from scripts.replicate_script import ReplicateWrapper

QApplication.setFont(QFont('Arial', 12))


class Thread(QThread):
    afterGenerated = Signal(str)
    errorGenerated = Signal(str)

    def __init__(self, wrapper, prompt):
        super().__init__()
        self.__wrapper = wrapper
        self.__prompt = prompt

    def run(self):
        try:
            image = self.__wrapper.get_image_response(prompt=self.__prompt)
            self.afterGenerated.emit(image)
        except Exception as e:
            self.errorGenerated.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__settings_ini = QSettings(os.path.join(ROOT_DIR, 'settings.ini'), QSettings.IniFormat)
        if not self.__settings_ini.contains('REPLICATE_API_TOKEN'):
            self.__settings_ini.setValue('REPLICATE_API_TOKEN', '')
            self.__settings_ini.setValue('model', 'stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b')
            self.__settings_ini.setValue('width', 768)
            self.__settings_ini.setValue('height', 768)
            self.__settings_ini.setValue('prompt', "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k")
            self.__settings_ini.setValue('negative_prompt', "ugly, deformed, noisy, blurry, distorted")
        self.__api_key = self.__settings_ini.value('REPLICATE_API_TOKEN', type=str)
        self.__model = self.__settings_ini.value('model', type=str)
        self.__width = self.__settings_ini.value('width', type=int)
        self.__height = self.__settings_ini.value('height', type=int)
        self.__prompt = self.__settings_ini.value('prompt', type=str)
        self.__negative_prompt = self.__settings_ini.value('negative_prompt', type=str)

        self.__wrapper = ReplicateWrapper(self.__api_key)

    def __initUi(self):
        self.setWindowTitle('PyQt Replicate Example')

        self.__apiWidget = ApiWidget(self.__api_key, self.__wrapper, self.__settings_ini, 'REPLICATE_API_TOKEN', True)
        self.__apiWidget.apiKeyAccepted.connect(self.__api_key_accepted)
        self.__apiWidget.notCheckApi()

        self.__imageWidget = ImageView()

        self.__modelCmbBox = QComboBox()
        self.__widthSpinBox = QSpinBox()
        self.__heightSpinBox = QSpinBox()
        self.__promptWidget = QTextEdit()
        self.__negativePromptWidget = QTextEdit()

        self.__promptWidget.setMaximumHeight(100)
        self.__negativePromptWidget.setMaximumHeight(100)

        lay = QFormLayout()
        lay.addRow('Model', self.__modelCmbBox)
        lay.addRow('Width', self.__widthSpinBox)
        lay.addRow('Height', self.__heightSpinBox)
        lay.addRow('Prompt', self.__promptWidget)
        lay.addRow('Negative Prompt', self.__negativePromptWidget)

        optionGrpBox = QGroupBox('Settings')
        optionGrpBox.setLayout(lay)

        self.__btn = QPushButton('Run')
        self.__btn.clicked.connect(self.__run)

        lay = QVBoxLayout()
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
        splitter.setStyleSheet(
            "QSplitterHandle {background-color: lightgray;}")
        splitter.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        lay = QVBoxLayout()
        lay.addWidget(self.__apiWidget)
        lay.addWidget(splitter)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setCentralWidget(mainWidget)

        self.__setAiEnabled(self.__wrapper.is_available())

    def __run(self):
        prompt = self.__promptWidget.text()
        self.__t = Thread(self.__wrapper, prompt)
        self.__t.started.connect(self.__started)
        self.__t.afterGenerated.connect(self.__afterGenerated)
        self.__t.finished.connect(self.__finished)
        self.__t.start()

    def __api_key_accepted(self, api_key, f):
        # Enable AI related features if API key is valid
        self.__setAiEnabled(f)

    def __setAiEnabled(self, f):
        self.__promptWidget.setEnabled(f)

    def __started(self):
        self.__btn.setEnabled(False)

    def __afterGenerated(self, data):
        self.__imageWidget.setBJson(data)

    def __errorGenerated(self, error: str):
        self.__chatBrowser.addMessage(self.__wrapper.get_message_obj('assistant', error))
        QMessageBox.critical(self, 'Error', error)

    def __finished(self):
        self.__btn.setEnabled(True)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    QApplication.setWindowIcon(QIcon('logo.png'))
    w = MainWindow()
    w.show()
    sys.exit(app.exec())