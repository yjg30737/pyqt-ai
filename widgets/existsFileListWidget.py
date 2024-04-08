import os
from collections import defaultdict

from qtpy.QtWidgets import QListWidget, QListWidgetItem


class ExistsFileListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self._basename_absname_dict = defaultdict(str)
        self._only_filename_flag = False
        self.__existsDialogDontAskAgainChecked = False

    def setOnlyFileName(self, flag: bool):
        self._only_filename_flag = flag
        self.setItemAsBaseName(flag)

    def setItem(self, item: QListWidgetItem):
        absname = item.text()
        basename = os.path.basename(absname)
        self._basename_absname_dict[basename] = absname
        if self._only_filename_flag:
            item.setText(basename)
        else:
            item.setText(absname)
        self.addItem(item)

    def setItemAsBaseName(self, flag: bool):
        self._only_filename_flag = flag
        items = [self.item(i) for i in range(self.count())]
        if flag:
            for item in items:
                absname = item.text()
                basename = os.path.basename(absname)
                item.setText(basename)
        else:
            for item in items:
                basename = item.text()
                absname = self._basename_absname_dict[basename]
                item.setText(absname)