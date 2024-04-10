import os
import sys

# Get the absolute path of the current script file

script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

from qtpy.QtWidgets import QLineEdit, QVBoxLayout, QMessageBox, QWidget, QMainWindow, QPushButton, QApplication
from qtpy.QtCore import QSettings, Signal, QThread
from qtpy.QtGui import QFont, QIcon

from settings import ROOT_DIR
from widgets.apiWidget import ApiWidget
from widgets.imageView import ImageView
from scripts.openai_script import GPTGeneralWrapper

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
        if not self.__settings_ini.contains('API_KEY'):
            self.__settings_ini.setValue('API_KEY', '')

        self.__api_key = self.__settings_ini.value('API_KEY', type=str)

        self.__wrapper = GPTGeneralWrapper(self.__api_key)

    def __initUi(self):
        self.setWindowTitle('PyQt GPT DALL-E Example')

        self.__apiWidget = ApiWidget(self.__api_key, self.__wrapper, self.__settings_ini)
        self.__apiWidget.apiKeyAccepted.connect(self.__api_key_accepted)
        self.__imageWidget = ImageView()

        self.__promptWidget = QLineEdit()
        self.__promptWidget.setPlaceholderText('Enter the prompt...')

        self.__btn = QPushButton('Run')
        self.__btn.clicked.connect(self.__run)

        lay = QVBoxLayout()
        lay.addWidget(self.__apiWidget)
        lay.addWidget(self.__promptWidget)
        lay.addWidget(self.__btn)
        lay.addWidget(self.__imageWidget)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setCentralWidget(mainWidget)

        self.__setAiEnabled(self.__wrapper.is_gpt_available())

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