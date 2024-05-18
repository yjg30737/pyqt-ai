import os, sys

# Get the absolute path of the current script file
script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

from qtpy.QtWidgets import QMainWindow, QPushButton, QApplication, QVBoxLayout, QWidget, QLabel, QMessageBox
from qtpy.QtCore import Qt, QSettings, QCoreApplication, QThread, Signal
from qtpy.QtGui import QFont


from constants import ROOT_DIR
from widgets.chatBrowser import ChatBrowser, PromptWidget
from widgets.apiWidget import ApiWidget
from scripts.openai_script import GPTAssistantWrapper
from widgets.tableWidget import TableWidget

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
            response = self.__wrapper.send_message(self.__text)
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

        self.__wrapper = GPTAssistantWrapper(self.__api_key)
        self.__assistant_list = self.__wrapper.get_assistants()

    def __initUi(self):
        self.setWindowTitle('PyQt GPT Assistant Example')

        self.__apiWidget = ApiWidget(self.__api_key, wrapper=self.__wrapper, settings=self.__settings_ini)
        self.__apiWidget.apiKeyAccepted.connect(self.__api_key_accepted)

        self.__chatBrowser = ChatBrowser()

        self.__promptWidget = PromptWidget()
        self.__promptTextEdit = self.__promptWidget.getTextEdit()
        self.__promptTextEdit.setPlaceholderText('Enter the prompt...')
        self.__promptWidget.sendPrompt.connect(self.__run)

        messages = self.__wrapper.get_conversations()
        self.__chatBrowser.setMessages(messages)

        columns = ['assistant_id', 'name', 'tools', 'model', 'instructions']

        self.__tableWidget = TableWidget(columns=columns)
        for obj in self.__assistant_list:
            self.__tableWidget.addRecord(obj)
        self.__tableWidget.selectedRecord.connect(self.__assistantSelected)

        self.__currentAssistantLbl = QLabel(f'Current Assistant:')
        self.__tableWidget.selectRow(0)

        self.__vbox = QVBoxLayout()
        self.__vbox.addWidget(self.__apiWidget)
        self.__vbox.addWidget(QLabel('Assistant'))
        self.__vbox.addWidget(self.__tableWidget)
        self.__vbox.addWidget(self.__currentAssistantLbl)
        self.__vbox.addWidget(self.__chatBrowser)
        self.__vbox.addWidget(self.__promptWidget)

        self.__widget = QWidget()
        self.__widget.setLayout(self.__vbox)

        self.setCentralWidget(self.__widget)

    def __assistantSelected(self, obj):
        self.__currentAssistantLbl.setText(f'Current Assistant: {obj["name"]}')
        self.__wrapper.set_current_assistant(obj['assistant_id'])

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


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())