import os
import sys

# Get the absolute path of the current script file
script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

os.environ['QT_API'] = 'pyside6'

from qtpy.QtGui import QGuiApplication, QFont, QIcon
from qtpy.QtWidgets import QHBoxLayout, QApplication, QLineEdit, QSizePolicy, QVBoxLayout, QWidget, QMainWindow, QPushButton, QApplication
from qtpy.QtCore import Qt, QSettings, Signal, QCoreApplication, QThread, Slot

from settings import ROOT_DIR
from widgets.chatBrowser import ChatBrowser, PromptWidget
from widgets.apiWidget import ApiWidget
from scripts.openai_script import GPTGeneralWrapper

QApplication.setFont(QFont('Arial', 12))


class Thread(QThread):
    afterGenerated = Signal(dict)
    errorGenerated = Signal(str)

    def __init__(self, wrapper, text):
        super(Thread, self).__init__()
        self.__wrapper = wrapper
        self.__text = text

    def run(self):
        try:
            args = self.__wrapper.get_arguments(cur_text=self.__text)
            response = self.__wrapper.get_text_response(args)
            self.afterGenerated.emit(response)
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

        # Set SQLite database path as default
        self.__wrapper = GPTGeneralWrapper(self.__api_key)

    def __initUi(self):
        self.setWindowTitle('PyQt GPT Chatbot Example')

        self.__apiWidget = ApiWidget(self.__api_key, self.__wrapper, self.__settings_ini)
        self.__apiWidget.apiKeyAccepted.connect(self.__api_key_accepted)

        self.__chatBrowser = ChatBrowser()

        self.__promptWidget = PromptWidget()
        self.__promptTextEdit = self.__promptWidget.getTextEdit()
        self.__promptTextEdit.setPlaceholderText('Enter the prompt...')
        self.__promptWidget.sendPrompt.connect(self.__run)

        messages = self.__wrapper.get_conversations()
        self.__chatBrowser.setMessages(messages)

        lay = QVBoxLayout()
        lay.addWidget(self.__apiWidget)
        lay.addWidget(self.__chatBrowser)
        lay.addWidget(self.__promptWidget)
        lay.setSpacing(0)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setCentralWidget(mainWidget)

        self.__setAiEnabled(self.__wrapper.is_gpt_available())

    def __run(self, text):
        self.__chatBrowser.addMessage(self.__wrapper.get_message_obj('user', text))

        self.__t = Thread(self.__wrapper, text)
        self.__t.started.connect(self.__started)
        self.__t.afterGenerated.connect(self.__afterGenerated)
        self.__t.errorGenerated.connect(self.__errorGenerated)
        self.__t.finished.connect(self.__finished)
        self.__t.start()

    def __api_key_accepted(self, api_key, f):
        # Enable AI related features if API key is valid
        self.__setAiEnabled(f)

    def __setAiEnabled(self, f):
        self.__promptWidget.setEnabled(f)

    def __started(self):
        pass
        # self.__btn.setEnabled(False)

    def __afterGenerated(self, response: dict):
        self.__chatBrowser.addMessage(response)

    def __errorGenerated(self, error: str):
        self.__chatBrowser.addMessage(self.__wrapper.get_message_obj('assistant', error))
        QMessageBox.critical(self, 'Error', error)

    def __finished(self):
        pass
        # self.__btn.setEnabled(True)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    QApplication.setWindowIcon(QIcon('logo.png'))
    w = MainWindow()
    w.show()
    sys.exit(app.exec())