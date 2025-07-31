import os
import sys

# Get the absolute path of the current script file
script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

os.environ["QT_API"] = "pyside6"

from qtpy.QtGui import QFont, QIcon
from qtpy.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QMainWindow,
    QApplication,
    QLabel,
    QSplitter,
    QTableWidgetItem,
    QMessageBox,
)
from qtpy.QtCore import Signal, QThread

from widgets.chatBrowser import ChatBrowser, PromptWidget
from widgets.addDelTableWidget import AddDelTableWidget
from scripts.ollama_script import OllamaWrapper

QApplication.setFont(QFont("Arial", 12))


class ChatThread(QThread):
    afterGenerated = Signal(dict)
    errorGenerated = Signal(str)

    def __init__(self, wrapper, text):
        super().__init__()
        self.__wrapper = wrapper
        self.__text = text

    def run(self):
        try:
            response = self.__wrapper.send_message(self.__text)
            response = self.__wrapper.get_message_obj("assistant", response.content)
            self.afterGenerated.emit(response)
        except Exception as e:
            self.errorGenerated.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__wrapper = OllamaWrapper()

    def __initUi(self):
        self.setWindowTitle("PyQt Ollama Chatbot Example")
        self.setMinimumSize(800, 600)

        self.__currentModelLbl = QLabel("Current Model: ")

        self.__leftWidget = AddDelTableWidget(
            "Models",
            columns=[
                {"name": "Model Name", "type": "str"},
                {"name": "Size", "type": "str"},
            ],
            checkable=True,
            is_download=True,
            wrapper=self.__wrapper,
        )
        self.__leftWidget.layout().setContentsMargins(5, 5, 5, 5)
        self.__leftWidget.added.connect(self.__showModels)
        self.__tableWidget = self.__leftWidget.getTableWidget()

        self.__chatBrowser = ChatBrowser()

        self.__promptWidget = PromptWidget()
        self.__promptTextEdit = self.__promptWidget.getTextEdit()
        self.__promptTextEdit.setPlaceholderText("Enter the prompt...")
        self.__promptWidget.sendPrompt.connect(self.__run)

        lay = QVBoxLayout()
        lay.addWidget(self.__currentModelLbl)
        lay.addWidget(self.__chatBrowser)
        lay.addWidget(self.__promptWidget)
        lay.setSpacing(2)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        splitter = QSplitter()
        splitter.addWidget(self.__leftWidget)
        splitter.addWidget(mainWidget)

        self.setCentralWidget(splitter)

        self.__showModels()

        if self.__tableWidget.rowCount() > 0:
            self.__tableWidget.selectRow(0)
            self.setCurrentModel()

        self.__tableWidget.itemSelectionChanged.connect(self.setCurrentModel)

    def setCurrentModel(self):
        model_name = self.__tableWidget.item(self.__tableWidget.currentRow(), 1).text()
        self.__currentModelLbl.setText(
            f"Current Model: {model_name if self.__tableWidget.rowCount() > 0 else 'None'}"
        )
        self.__wrapper.set_model_name(model_name)

    def __showModels(self):
        models = self.__wrapper.get_ollama_models()
        self.__leftWidget.getTableWidget().clearContents()
        self.__leftWidget.getTableWidget().setRowCount(0)

        for model in models:
            model_name = model["NAME"]
            model_size = model["SIZE"]
            row_position = self.__leftWidget.getTableWidget().rowCount()
            self.__leftWidget.getTableWidget().insertRow(row_position)
            self.__leftWidget.getTableWidget().setItem(
                row_position, 1, QTableWidgetItem(model_name)
            )
            self.__leftWidget.getTableWidget().setItem(
                row_position, 2, QTableWidgetItem(model_size)
            )

    def __run(self, text):
        self.__chatBrowser.addMessage(self.__wrapper.get_message_obj("user", text))

        self.__chat_thread = ChatThread(self.__wrapper, text)
        self.__chat_thread.started.connect(self.__started)
        self.__chat_thread.afterGenerated.connect(self.__afterGenerated)
        self.__chat_thread.errorGenerated.connect(self.__errorGenerated)
        self.__chat_thread.finished.connect(self.__finished)
        self.__chat_thread.start()

    def __started(self):
        pass

    def __afterGenerated(self, response: dict):
        self.__chatBrowser.addMessage(response)

    def __errorGenerated(self, error: str):
        self.__chatBrowser.addMessage(
            self.__wrapper.get_message_obj("assistant", error)
        )
        QMessageBox.critical(self, "Error", error)

    def __finished(self):
        self.__promptTextEdit.clear()
        self.__promptTextEdit.setFocus()

        if hasattr(self, "__chat_thread"):
            self.__chat_thread.deleteLater()
            del self.__chat_thread


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    QApplication.setWindowIcon(QIcon("logo.png"))
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
