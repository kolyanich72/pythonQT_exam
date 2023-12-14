from PySide6 import QtCore, QtWidgets, QtGui
from common_info import Common_info_window  # , cur_proc, syst_info
from cur_proc import Window as Wind_proc
from net_info import Net_info_window
import wmi, time


class Window(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowTitleHint)
        self.net = Net_info_window()
        self._common_info = Common_info_window()
        self._cur_proc = Wind_proc()

        self.initUi()
        self.initSignal()

    def initSignal(self):
        self._common_info.close_but.clicked.connect(self._close_but_clicked)
        self.delay_spinBox.valueChanged.connect(self.setDelay)

    def setDelay(self, delay):
        self._common_info._thread.setDelay(delay)
        self._cur_proc._thread.setDelay(delay)
        self.net._thread.setDelay(delay)

    def _close_but_clicked(self):
        self._common_info._thread.setStatus(False)

        self.close()

    def initUi(self) -> None:
        flags = QtCore.Qt.WindowFlags()

        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setStyleSheet("background-color: lightgray")
        self.tabWidget.setMinimumWidth(600)

        self.delay_Label = QtWidgets.QLabel("таймер обновления")
        self.delay_spinBox = QtWidgets.QSpinBox()

        self.comn_info_label = QtWidgets.QVBoxLayout()
        self.comn_info_label.addLayout(self._common_info.main_layot)

        self.proc_info_label = QtWidgets.QPlainTextEdit('запущенные процессы и службы')
        self.proc_info_label.setReadOnly(True)
        self.system_info_net = QtWidgets.QPlainTextEdit('сеть')

        self.system_info_net.setReadOnly(True)

        delay_Layout = QtWidgets.QHBoxLayout()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.tabWidget.addTab(self._common_info.common_info_block, 'общая информация')
        self.tabWidget.addTab(self._common_info.info_static_bat_info, 'системная информация')

        self.tabWidget.addTab(self._cur_proc.tableView, 'запущенные процессы и службы')

        self.tabWidget.addTab(self.net, 'сеть')

        self.delay_spinBox.setMinimum(5)

        delay_Layout.addWidget(self.delay_Label)
        delay_Layout.addWidget(self.delay_spinBox)

        self.main_layout.addLayout(delay_Layout)
        self.main_layout.addWidget(self.tabWidget)
        self.main_layout.addWidget(self._common_info.close_but)
        self.setLayout(self.main_layout)

    #   self.setLayout(self._common_info.main_layot)


if __name__ == "__main__":
    app = QtWidgets.QApplication()

    window = Window()
    window.show()

    app.exec()
