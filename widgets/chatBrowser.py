from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QTextEdit


class ChatBrowser(QScrollArea):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignTop)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        widget = QWidget()
        widget.setLayout(lay)
        self.setWidget(widget)
        self.setWidgetResizable(True)

    def setMessages(self, messages):
        for message in messages:
            self.addMessage(message['content'], message['role'])

    def addMessage(self, content, role):
        chatLbl = QLabel(content)
        chatLbl.setWordWrap(True)
        chatLbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        if role == 'user':
            chatLbl.setStyleSheet('QLabel { padding: 1em }')
        else:
            chatLbl.setStyleSheet('QLabel { background-color: #DDD; padding: 1em }')
        self.widget().layout().addWidget(chatLbl)

    def event(self, e):
        if e.type() == 43:
            self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().maximum())
        return super().event(e)

    def getAllText(self):
        all_text_lst = []
        lay = self.widget().layout()
        if lay:
            for i in range(lay.count()):
                if lay.itemAt(i) and lay.itemAt(i).widget():
                    widget = lay.itemAt(i).widget()
                    if isinstance(widget, QLabel):
                        all_text_lst.append(widget.text())

        return '\n'.join(all_text_lst)


class TextEditPrompt(QTextEdit):
    returnPressed = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initUi()

    def __initUi(self):
        self.setStyleSheet('QTextEdit { border: 1px solid #AAA; } ')
        self.setAcceptRichText(False)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
            if e.modifiers() == Qt.ShiftModifier:
                return super().keyPressEvent(e)
            else:
                self.returnPressed.emit(self.toPlainText())
        else:
            return super().keyPressEvent(e)


class PromptWidget(QWidget):
    sendPrompt = Signal(str)

    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.__textEdit = TextEditPrompt()
        self.__textEdit.textChanged.connect(self.updateHeight)
        self.__textEdit.returnPressed.connect(self.__sendPrompt)
        lay = QHBoxLayout()
        lay.addWidget(self.__textEdit)
        lay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(lay)
        self.updateHeight()

    def __sendPrompt(self, text):
        self.sendPrompt.emit(text)
        self.__textEdit.clear()

    def updateHeight(self):
        document = self.__textEdit.document()
        height = document.size().height()
        self.setMaximumHeight(int(height + document.documentMargin()))

    def getTextEdit(self):
        return self.__textEdit

