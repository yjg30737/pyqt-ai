from qtpy.QtWidgets import QDialog, QFormLayout, QVBoxLayout, QLineEdit, QFrame, QPushButton, QHBoxLayout, QWidget, \
    QComboBox, QLineEdit, QSpinBox, QTextEdit, QDoubleSpinBox
from qtpy.QtCore import Qt

from scripts.qt_script import get_form_layout


class InputDialog(QDialog):
    def __init__(self, title, attributes_list, parent=None):
        """
        :param title: Title of the dialog
        :param attributes: Attributes of the dialog.
        Looks like
        [
            {'name': 'Name', 'attribute': '', 'default': Math Tutor, 'selection': []},
            ...
        ]
        :param parent:
        """
        super().__init__(parent)
        self.__initVal(attributes_list)
        self.__initUi(title)

    def __initVal(self, attributes_list):
        self.__input_attr = attributes_list
        self.__output_attr = {obj['attribute']: obj['default'] for obj in self.__input_attr}

    def __initUi(self, title):
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)

        self.__lay, self.__input_attr = get_form_layout(self.__input_attr)

        mainWidget = QWidget()
        mainWidget.setLayout(self.__lay)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)

        self.__okBtn = QPushButton('OK')
        self.__okBtn.clicked.connect(self.accept)

        cancelBtn = QPushButton('Cancel')
        cancelBtn.clicked.connect(self.close)

        lay = QHBoxLayout()
        lay.addWidget(self.__okBtn)
        lay.addWidget(cancelBtn)
        lay.setAlignment(Qt.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        okCancelWidget = QWidget()
        okCancelWidget.setLayout(lay)

        lay = QVBoxLayout()
        lay.addWidget(mainWidget)
        lay.addWidget(sep)
        lay.addWidget(okCancelWidget)

        self.setLayout(lay)

        self.__setAccept()

    def getAttribute(self):
        return self.__output_attr

    # FIXME
    # Fix the problem which is that the OK button is enabled even if the required fields are not filled
    def __setAccept(self):
        # Enable OK button if all required fields are filled
        # Get widgets in the form layout
        for i, obj in enumerate(self.__input_attr):
            widget = obj['widget']
            v = ''
            if isinstance(widget, QComboBox) and widget.currentText().strip():
                v = widget.currentText().strip()
            elif isinstance(widget, QLineEdit) and widget.text().strip():
                v = widget.text().strip()
            elif isinstance(widget, QSpinBox) and widget.value():
                v = widget.value()
            elif isinstance(widget, QDoubleSpinBox) and widget.value():
                v = widget.value()
            elif isinstance(widget, QTextEdit) and widget.toPlainText().strip():
                v = widget.toPlainText().strip()
            elif isinstance(widget, QCheckBox) and widget.isChecked():
                v = widget.isChecked()
            elif isinstance(widget, QGroupBox):
                v = self.__setAccept()
            if not v:
                self.__okBtn.setEnabled(False)
                return
            else:
                self.__output_attr[obj['attribute']] = v
        self.__okBtn.setEnabled(True)