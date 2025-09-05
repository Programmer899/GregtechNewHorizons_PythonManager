import win32serviceutil
import win32service
import win32event
import servicemanager
import subprocess
import sys
import os
from pathlib import Path

class WebMonitorService(win32serviceutil.ServiceFramework):
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
        servicemanager.LogInfoMsg("WebMonitorService is starting...")

        # python_exe = sys.executable  # Same as python running this script
        python_exe = "c:\\Python311\\python.exe"
        script_cwd = f"{sys.path[0]}\\..\\"

        script_path = f"{script_cwd}main.py"
        log_file = f"{script_cwd}WebService\\service.log"

        # flags = (
        #     subprocess.CREATE_BREAKAWAY_FROM_JOB
        #     | subprocess.CREATE_NEW_PROCESS_GROUP
        #     | subprocess.CREATE_NEW_CONSOLE
        # )

        Path(log_file).touch()

        command = [python_exe, script_path]

        with open(log_file, "w") as f:
            # f.write(python_exe)

            self.proc = subprocess.Popen(
                command,
                stdout=f,
                stderr=f,
                cwd=script_cwd,  # set working directory
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                # creationflags=flags,
                bufsize=1,
                universal_newlines=True
            )

            f.close()

        # Vänta tills vi får stop-event
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

        servicemanager.LogInfoMsg("WebMonitorService is stopped.")

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(WebMonitorService)
