import base64

from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QGraphicsScene, QGraphicsView, QMenu, QAction, QFileDialog


class ImageView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.__aspectRatioMode = Qt.KeepAspectRatio
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__scene = QGraphicsScene()
        self.__item = ''
        self.setScene(self.__scene)

    def __initUi(self):
        self.__initAction()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__prepare_menu)

    def __initAction(self):
        self.__saveAction = QAction("Save Image", self)
        self.__saveAction.triggered.connect(self.__saveImage)
        self.__saveAction.setShortcut('Ctrl+S')
        self.__saveAction.setShortcutContext(Qt.WidgetShortcut)
        self.__saveAction.setEnabled(False)

    def __saveImage(self):
        filename = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if filename[0]:
            self.__scene.clearSelection()
            image = self.__scene.items()[0]
            pixmap = QPixmap(image.pixmap())
            pixmap.save(filename[0])

    def __prepare_menu(self, pos):
        menu = QMenu(self)
        menu.addAction(self.__saveAction)
        menu.exec_(self.mapToGlobal(pos))

    def setBJson(self, b64_json: str):
        self.__scene.clear()
        data = base64.b64decode(b64_json)
        self.__setPixmap(data, is_b64=True)

    def setFilename(self, filename: str):
        # Clear the scene before adding a new image
        if self.__item:
            self.__scene.removeItem(self.__item)
        self.__scene.clear()
        self.__setPixmap(filename)

    def __setPixmap(self, data, is_b64=False):
        p = QPixmap()
        if is_b64:
            p.loadFromData(data)
        else:
            # if filename
            p.load(data)
        self.__scene.setSceneRect(0, 0, p.width(), p.height())
        self.__item = self.__scene.addPixmap(p)
        self.__item.setTransformationMode(Qt.SmoothTransformation)

        self.__saveAction.setEnabled(True)

        self.fitInView(self.__item, self.__aspectRatioMode)

    def setAspectRatioMode(self, mode):
        self.__aspectRatioMode = mode

    def resizeEvent(self, e):
        if self.__item:
            self.fitInView(self.sceneRect(), self.__aspectRatioMode)
        return super().resizeEvent(e)