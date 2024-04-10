import os
from pathlib import Path
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QVBoxLayout, QWidget, QListWidget, QLabel, QSizePolicy, QSpacerItem, QHBoxLayout, QPushButton, QFileDialog

from widgets.imageView import ImageView


class FileListWidget(QWidget):
    def __init__(self, label):
        super().__init__()
        self._init_values()
        self._init_ui(label)

    def _init_values(self):
        self.supported_extensions = ['.jpg', '.png']

    def _init_ui(self, label):
        self._setup_list_widget()
        self._setup_buttons()
        self._setup_layout(label)
        self._toggle_delete_button()
        self.setAcceptDrops(True)

    def _setup_list_widget(self):
        self.list_widget = QListWidget()
        self.list_widget.doubleClicked.connect(self._show_image)

    def _setup_buttons(self):
        self.add_button = QPushButton('Add')
        self.delete_button = QPushButton('Delete')
        self.add_button.clicked.connect(self._read_files)
        self.delete_button.clicked.connect(self._delete_selected_item)

    def _setup_layout(self, label):
        header_layout = self._create_header_layout(label)
        main_layout = QVBoxLayout()
        main_layout.addWidget(header_layout)
        main_layout.addWidget(self.list_widget)
        self.setLayout(main_layout)

    def _create_header_layout(self, label):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        layout.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        layout.addWidget(self.add_button)
        layout.addWidget(self.delete_button)
        layout.setAlignment(Qt.AlignRight)
        layout.setContentsMargins(0, 0, 0, 0)
        header_widget = QWidget()
        header_widget.setLayout(layout)
        return header_widget

    def _toggle_delete_button(self):
        self.delete_button.setEnabled(self.list_widget.count() > 0)

    def _delete_selected_item(self):
        try:
            self.list_widget.takeItem(self.list_widget.row(self.list_widget.currentItem()))
            self._toggle_delete_button()
        except Exception as e:
            print(e)

    def _show_image(self):
        self.__image_viewer = ImageView()
        self.__image_viewer.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.__image_viewer.setWindowFlag(Qt.WindowCloseButtonHint)
        self.__image_viewer.setWindowTitle('View Image')
        self.__image_viewer.setFilename(self.list_widget.currentItem().text())
        self.__image_viewer.show()

    def _read_files(self):
        file_dialog = QFileDialog(self, 'Find', os.path.expanduser('~'), 'Image Files (*.jpg *.png)')
        selected_files, _ = file_dialog.getOpenFileNames()
        if selected_files:
            for filename in selected_files:
                if Path(filename).suffix in self.supported_extensions:
                    self.list_widget.addItem(filename)
        self._toggle_delete_button()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()

    def dragMoveEvent(self, event):
        pass

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls() if Path(url.toLocalFile()).suffix in self.supported_extensions]
        self.list_widget.addItems(files)
        super().dropEvent(event)

    def get_filenames(self):
        return [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
