import psutil
from typing import Literal

def findApplication(serchAlgorythm: Literal["Name", "NameUnsafe", "CommandLine", "PID"] = "Name", checker: str = "") -> psutil.Process | None:
    process = None

    for pid in psutil.pids():
        if not psutil.pid_exists(pid):
            continue
        
        try:
            proc = psutil.Process(pid)

            match serchAlgorythm:
                case "Name":
                    if proc.name() == checker:
                        process = proc

                case "NameUnsafe":
                    if proc.name().lower().find(checker.lower()) != -1:
                        process = proc

                case "CommandLine":
                    if f"{proc.cmdline()}".find(checker) != -1:
                        process = proc

                case "PID":
                    if f"{proc.pid}" == checker:
                        process = proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            pass
    
    if process != None:
        return process
    else:
        return None
