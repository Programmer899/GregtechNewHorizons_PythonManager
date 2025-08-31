import win32serviceutil
import win32service
import win32event
import servicemanager
import subprocess
import sys
import os

class MyPythonService(win32serviceutil.ServiceFramework):
    _svc_name_ = "GTNH_Web_Monitor"
    _svc_display_name_ = "GregtechNewHorizons Web Monitor"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.proc = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.proc:
            self.proc.terminate()  # försök stänga ditt script
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("MyPythonService is starting...")

        python_exe = sys.executable  # samma python som kör tjänsten
        script_path = r"C:\Users\lindg\Programming\Webb\GregtechNewHorizons\main.py"
        log_file = r"C:\\Users\\lindg\\Programming\\Webb\\GregtechNewHorizons\\WebService\\service.log"

        flags = (
            subprocess.CREATE_BREAKAWAY_FROM_JOB
            | subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.CREATE_NEW_CONSOLE
        )

        # # command = ["powershell.exe", f"cd 'C:\Users\lindg\Programming\Webb\GregtechNewHorizons'; $host.ui.RawUI.WindowTitle = '{self._svc_name_}'; & '{script_path}'"]
        # command = [f'{python_exe}', f'cd "C:\\Users\\lindg\\Programming\\Webb\\GregtechNewHorizons"; $host.ui.RawUI.WindowTitle = "{self._svc_name_}"; & "{script_path}"']

        # # starta ditt skript som subprocess
        # with open(log_file, "a") as f:
        #     self.proc = subprocess.Popen(
        #         command,
        #         creationflags=flags,
        #         stdout=f,
        #         stderr=f,
        #         bufsize=1,
        #         universal_newlines=True
        #     )

        script_dir = "C:\\Users\\lindg\\Programming\\Webb\\GregtechNewHorizons"

        command = ['C:\\WINDOWS\\py.exe', 'C:\\Users\\lindg\\Programming\\Webb\\GregtechNewHorizons\\main.py']

        with open(log_file, "a") as f:
            self.proc = subprocess.Popen(
                # [python_exe, "C:\\Users\\lindg\\Programming\\Webb\\GregtechNewHorizons\\main.py"],
                command,
                stdout=f,
                stderr=f,
                cwd=script_dir,  # set working directory
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                # creationflags=flags,
                bufsize=1,
                universal_newlines=True
            )

            f.close()

        # Vänta tills vi får stop-event
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

        servicemanager.LogInfoMsg("MyPythonService is stopped.")


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MyPythonService)
