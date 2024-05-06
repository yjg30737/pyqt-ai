from qtpy.QtWidgets import QTableWidget, QTableWidgetItem
from qtpy.QtCore import Signal


class TableWidget(QTableWidget):
    selectedRecord = Signal(dict)

    def __init__(self, parent=None, columns=None):
        super(TableWidget, self).__init__(parent)
        self.__initVal(columns)
        self.__initUi(columns)

    def __initVal(self, columns=None):
        self.__column_map = {key: index for index, key in enumerate(columns)}

    def __initUi(self, columns):
        self.setColumnCount(len(columns))
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.setHorizontalHeaderLabels(columns)
        self.setEditTriggers(self.NoEditTriggers)
        self.setSelectionBehavior(self.SelectRows)
        self.itemSelectionChanged.connect(self.__onSelectionChanged)

    def addRecord(self, record):
        row_position = self.rowCount()
        self.insertRow(row_position)
        for key, value in record.items():
            if key in self.__column_map:
                column_index = self.__column_map[key]
                # For the 'tools' column, which contains a list, convert it to a string representation
                if key == 'tools':
                    value = str(value)
                self.setItem(row_position, column_index, QTableWidgetItem(str(value)))

    def getRecord(self, row):
        record = {}
        for key, index in self.__column_map.items():
            if self.item(row, index) is not None:
                record[key] = self.item(row, index).text()
            else:
                record[key] = ''
        return record

    def __onSelectionChanged(self):
        selected_row = self.currentRow()
        if selected_row != -1:
            record = self.getRecord(selected_row)
            self.selectedRecord.emit(record)