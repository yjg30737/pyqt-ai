import os
import sys

# Get the absolute path of the current script file
script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

from qtpy.QtGui import QGuiApplication, QFont, QIcon
from qtpy.QtWidgets import QHBoxLayout, QApplication, QLineEdit, QSizePolicy, QSplitter, QVBoxLayout, QWidget, QMainWindow, QPushButton, QApplication, QMessageBox
from qtpy.QtCore import Qt, QSettings, Signal, QCoreApplication, QThread, Slot

from constants import ROOT_DIR
from widgets.chatBrowser import ChatBrowser, PromptWidget
from widgets.apiWidget import ApiWidget
from scripts.llamaindex_script import GPTLlamaIndexWrapper
from widgets.dirListWidget import DirListWidget

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
            response = self.__wrapper.get_llamaindex_response_from_documents(self.__text)
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
        self.__wrapper = GPTLlamaIndexWrapper(self.__api_key)

    def __initUi(self):
        self.setWindowTitle('PyQt GPT Chatbot Example')

        self.__apiWidget = ApiWidget(self.__api_key, self.__wrapper, self.__settings_ini)
        self.__apiWidget.apiKeyAccepted.connect(self.__api_key_accepted)

        self.__chatBrowser = ChatBrowser()

        self.__promptWidget = PromptWidget()
        self.__promptTextEdit = self.__promptWidget.getTextEdit()
        self.__promptTextEdit.setPlaceholderText('Enter the prompt...')
        self.__promptWidget.sendPrompt.connect(self.__run)

        self.__listWidget = DirListWidget()
        self.__listWidget.onDirectorySelected.connect(self.__onDirectorySelected)

        messages = self.__wrapper.get_conversations()
        self.__chatBrowser.setMessages(messages)

        lay = QVBoxLayout()
        lay.addWidget(self.__chatBrowser)
        lay.addWidget(self.__promptWidget)

        chatWidget = QWidget()
        chatWidget.setLayout(lay)

        splitter = QSplitter()
        splitter.addWidget(self.__listWidget)
        splitter.addWidget(chatWidget)
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)
        splitter.setSizes([500, 500])
        splitter.setStyleSheet(
            "QSplitterHandle {background-color: lightgray;}")
        splitter.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        lay = QVBoxLayout()
        lay.addWidget(self.__apiWidget)
        lay.addWidget(splitter)
        lay.setSpacing(0)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setCentralWidget(mainWidget)
        self.__setAiEnabled(False)

    def __onDirectorySelected(self, directory):
        self.__wrapper.set_directory(directory)
        self.__wrapper.set_query_engine(False)
        self.__setAiEnabled(True)

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