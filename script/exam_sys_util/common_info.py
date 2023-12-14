import psutil, platform
import time
from PySide6 import QtWidgets, QtCore
import wmi


def format_memory(n):
    suff = ["Б", "КБ", "МБ", "ГБ", "ТБ"]
    pref = 0
    for i in range(len(suff) - 1):
        if n > 1024:
            n = n / 1024
            pref = i + 1
    return (f"{n:.2f}{suff[pref]}")


class SystemInfo(QtCore.QThread):
    systemSignal = QtCore.Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.delay = 3
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

    def run(self) -> None:  # TODO переопределить метод run

        while self.status:
            cpu_value = psutil.cpu_percent()
            cpu_memo = psutil.virtual_memory()
            disk_ = wmi.WMI().Win32_LogicalDisk()

            q7 = psutil.sensors_battery()
            bat_status = "от внутренней батареи" if not q7.power_plugged else "от сети"
            bat_info = f'зарядка- {q7.percent}%\n' \
                       f'питание  {bat_status}'

            cpu_memo_total = cpu_memo.total
            cpu_memo_used = cpu_memo.used
            cpu_memo_available = cpu_memo.available
            ram_value = psutil.virtual_memory().percent
            data = []
            data.append(cpu_memo_total)
            data.append(cpu_memo_used)
            data.append(cpu_memo_available)
            data.append(cpu_value)
            data.append(ram_value)
            data.append(bat_info)
            self.systemSignal.emit(data)
            time.sleep(self.delay)


class Common_info_window(QtWidgets.QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._clock = time.strftime("%H:%M:%S %d %b %Y %a", time.localtime())
        self.cpu_thread = psutil.cpu_percent()
        #  self.set_virt_memo()
        self._disk = wmi.WMI().Win32_LogicalDisk()
        self._thread = SystemInfo()
        self._user = psutil.users()
        self.initUI()
        self.initSignal()

    def initSignal(self):
        self._thread.systemSignal.connect(
            lambda data: self._info(data))
        self.close_but.clicked.connect(self._close_but_clicked)

    def _close_but_clicked(self):
        self._thread.setStatus(False)

        self.close()

    def _info(self, data):
        str_ = f'доступная оперативная память: {format_memory(data[0])}\n' \
               f'используемая оперативная память {format_memory(data[1])}\n' \
               f'доступная свободная оперативная память: {format_memory(data[2])}\n' \
               f'процент загрузки процессора: {data[3]}%\n' \
               f'процент использования памяти: {data[4]}%\n' \
               f'{data[5]}'
        self.info_static_bat_info.setPlainText(str_)

    def set_virt_memo(self):
        self.cpu_memo = psutil.virtual_memory()

    def initUI(self):
        self.info_time_block = QtWidgets.QPlainTextEdit()
        self.info_static_bat_info = QtWidgets.QPlainTextEdit()
        self.info_static_disk_info = QtWidgets.QPlainTextEdit()
        self.close_but = QtWidgets.QPushButton("закрыть")
        syst_name = platform.system()
        user_info = self._user[0]

        self.common_info_block = QtWidgets.QLabel()

        self.info_time_block.appendPlainText(f"текущее время - {self._clock}\n")  ##подключить

        self.common_info_block.setText(
            f'текущий пользователь: {user_info.name}\n'
            f'время начала работы : {time.strftime("%d %b %Y %H:%M:%S", time.strptime(str(time.ctime(user_info.started))))}\n\n'
            f'операционная система: {syst_name}\n'
            f'версия:               {platform.version()}\n'
            f'номер релиза:         {platform.release()}\n'
            f'разрядность:          {platform.architecture()[0]}\n\n'
            f'процессор:\n'
            f'{platform.processor()}\n'
            f'количество ядер         {psutil.cpu_count(logical=False)}\n'
            f'количество потоков   {psutil.cpu_count()}\n'
            f'частота работы           {psutil.cpu_freq(percpu=False).current / 1000}ГГц\n\n'
            f'{self._disk_info()}'
            )

        layot1 = QtWidgets.QHBoxLayout()

        layot1.addWidget(self.info_static_bat_info)

        self.main_layot = QtWidgets.QVBoxLayout()
        self.main_layot.addLayout(layot1)
        self.main_layot.addWidget(self.common_info_block)
        self.main_layot.addWidget(self.close_but)
        self.setLayout(self.main_layot)

    def _disk_info(self):
        ###  в поток по таймеру
        str_ = ''
        i = self._disk[0]
        str_ += f"имя устройства          - {i.SystemName}\n" \
                f"производитель          - {i.VolumeName}\n" \
                f"серийный номер       - {i.VolumeSerialNumber}\n" \
                f"тип носителя             - {i.Description}\n" \
                f"системное имя          - {i.DeviceID}\n" \
                f"файловая система     - {i.FileSystem}\n" \
                f"свободный объем памяти - {format_memory(int(i.FreeSpace))}\n"
        return str_


if __name__ == "__main__":
    app = QtWidgets.QApplication()

    window = Common_info_window()
    window.show()

    app.exec()
