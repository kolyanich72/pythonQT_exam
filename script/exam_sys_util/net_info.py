import psutil, time
from PySide6 import QtWidgets, QtCore
from common_info import format_memory


class SystemInfoTread(QtCore.QThread):
    systemSignal = QtCore.Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.delay = 5
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
        print(self.delay, self.status, "  net")

    def run(self) -> None:  # TODO переопределить метод run

        while self.status:
            q1 = psutil.net_io_counters(pernic=True, nowrap=True)
            collect_info_dict = {}
            key_list = []
            for i in psutil.net_if_addrs():
                if i == 'Loopback Pseudo-Interface 1':
                    continue
                else:
                    key_list.append(i)

            for interface_name, interface_address in psutil.net_if_addrs().items():
                if interface_name == 'Loopback Pseudo-Interface 1':
                    continue
                else:
                    collect_info_dict[interface_name] = {
                        'mac': interface_address[0].address.replace("-", ":"),
                        'ipv4': interface_address[1].address,
                        'ipv6': interface_address[2].address}
            ## передача данных интернет

            for key_name in key_list:
                collect_info_dict[key_name]["_sent"] = format_memory(q1[key_name].bytes_sent)
                collect_info_dict[key_name]["_recv"] = format_memory(q1[key_name].bytes_recv)
                collect_info_dict[key_name]["packets_sent"] = q1[key_name].packets_sent
                collect_info_dict[key_name]["packets_recv"] = q1[key_name].packets_recv
                collect_info_dict[key_name]["err_recv"] = q1[key_name].errin
                collect_info_dict[key_name]["err_sent"] = q1[key_name].errout

            self.systemSignal.emit(collect_info_dict)
            time.sleep(self.delay)


class Net_info_window(QtWidgets.QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._thread = SystemInfoTread()
        self.initUI()
        self.initSignal()

    def initUI(self):
        self.info_net_info = QtWidgets.QPlainTextEdit()
        self.layout_ = QtWidgets.QVBoxLayout()

        self.layout_.addWidget(self.info_net_info)
        self.setLayout(self.layout_)

    def initSignal(self):
        self._thread.systemSignal.connect(lambda data: self._info_load(data))

    def _info_load(self, data: dict):
        str_ = ''
        self.info_net_info.clear()
        for k, v in data.items():
            str_ += f"\nсоединение: {k}\n" \
                   f"mac: {v['mac']}\nipv4: {v['ipv4']}\nipv6: {v['ipv6']}\nданные отправка: {v['_sent']}\nданные получение: {v['_recv']}\nпакеты отправка: {v['packets_sent']}\nпакеты получение: {v['packets_recv']}\nошибки при получении: {v['err_recv']}\nошибки при отправки: {v['err_sent']}\n"
        self.info_net_info.setPlainText(str_)

      #  self.info_net_info.setPlainText(str_)


if __name__ == "__main__":
    app = QtWidgets.QApplication()

    window = Net_info_window()
    window.show()

    app.exec()
