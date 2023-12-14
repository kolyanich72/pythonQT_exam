from PySide6 import QtCore, QtWidgets, QtGui

import wmi, time


class SystemInfoTread(QtCore.QThread):
    systemSignal = QtCore.Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.delay = 15
        self.status = True
        self.start()

    def setStatus(self, status) -> None:
        self.status = status

        if not self.status:
            self.terminate()

    def setDelay(self, delay):
        if delay == 0:
            self.status = 0
        self.delay = delay
        print(self.delay, self.status, "  proc")

    def run(self) -> None:
        print("RUN")
        while self.status:

            proc = wmi.WMI().Win32_Process()
            data = []

            for i in proc:

                act_list = []
                act_list.append(i.Name)
                act_list.append(i.ProcessId)
                type_ = "фоновый процесс"
                try:
                    d = i.ExecutablePath
                    if d:
                        type_ = "приложение"
                except:
                    type_ = "фоновый процесс"
                act_list.append(type_)
                data.append(act_list)

            self.systemSignal.emit(data)
            time.sleep(self.delay)


class Window(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._thread = SystemInfoTread()
        self.initTableModel()

        self.initUi()
        self.initSignal()

    def initUi(self) -> None:
        self.tableView = QtWidgets.QTableView()
        self.tableView.setModel(self.tableModel)

        self.tableView.selectionModel().currentChanged.connect(self.itemSelectionChanged)
        self.tableView.setMinimumWidth(500)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.tableView)
        # self.tableView.resizeColumnsToContents()
        self.setLayout(layout)

    def initSignal(self):
        self._thread.systemSignal.connect(lambda data: self._info_table(data))

    def _info_table(self, data):
        self.tableModel.clear()

        for i in data:
            item2 = QtGui.QStandardItem(str(i[0]))
            item2.setEditable(False)

            item3 = QtGui.QStandardItem(str(i[1]))
            item3.setEditable(False)
            item4 = QtGui.QStandardItem(str(i[2]))
            item4.setEditable(False)
            self.tableModel.appendRow([item2, item3, item4])

        self.tableModel.setHorizontalHeaderLabels(["-           имя процесса          -",
                                                   "-           Id процесса           -",
                                                   "-           тип процесса          -"])
        self.tableView.resizeColumnsToContents()

    def initTableModel(self) -> None:
        self.tableModel = QtGui.QStandardItemModel()

        item1 = QtGui.QStandardItem("идет загрузка")
        item1.setEditable(False)
        self.tableModel.appendRow([item1, item1, item1])
        self.tableModel.setHorizontalHeaderLabels(["-            имя процесса          -",
                                                   "-            Id процесса           -",
                                                   "-            тип процесса          -"])

    def itemSelectionChanged(self, item: QtCore.QModelIndex) -> None:
        """
        Действие при нажатии на элемент в таблице

        :param item: текущий элемент
        :return: None
        """

        # print(self.itemSelectionChanged)
        # print(item.row())
        # print(item.column())
        #
        # print(item.data(0))
        pass

    def tableViewDataChanged(self, item) -> None:
        """
        Действие при изменении данных в таблице

        :param item: текущий элемент
        :return: None
        """

        # print(self.tableViewDataChanged)
        # model = self.tableView.model()
        # id_ = model.index(item.row(), 0)
        # print()
        # print()
        # print(item.row())
        # print(item.column())
        #
        # print()
        # print(id_.data(0))
        # print(item.data(0))
        #
        # if item.column() == 1:
        #     pass
        #     # do query_1
        # elif item.column() == 2:
        #     pass
        # do query_2
        # back for db
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication()

    window = Window()
    window.show()

    app.exec()
