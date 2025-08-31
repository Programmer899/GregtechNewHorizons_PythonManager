from pathlib import Path
from typing import Literal
import psutil

class Memorization():
    def __init__(self, pidsDir: Path):#, readMode: Literal["normal", "text"] = "normal"):
        self.__pidsDir: Path = pidsDir
        # self.readMode: Literal["normal", "text"] = readMode
    
    def Memorize(self, pid: int, process_name: str, inputFile: Path = Path(""), outputFile: Path = Path(""), errFile: Path = Path("")):
        if self.__pidsDir.exists():
            pidPath = Path(f"{self.__pidsDir}/{pid}.txt")
            if not pidPath.exists():
                filesString = ""

                if inputFile != "":
                    filesString += f'|{inputFile}'
                else:
                    filesString += '|""'

                if outputFile != "":
                    filesString += f'|{outputFile}'
                else:
                    filesString += '|""'

                if errFile != "":
                    filesString += f'|{errFile}'
                else:
                    filesString += '|""'

                with Path.open(pidPath, "w") as f:
                    f.write(f"{pid}|{process_name}{filesString}")
                    f.close()
                
                return f"Process has been memorized under: {pid}|{process_name}{filesString}", 1
            else:
                return "Pid is already in memory", 2
        else:
            return "Root directory for pids has not been set", 0
    
    def GetMemory(self, pid: int, process_name: str) -> tuple[str, int, Path, Path, Path]:
        if self.__pidsDir.exists():
            pidPath = Path(f"{self.__pidsDir}/{pid}.txt")
            # print(f"Pid path was: {pidPath}")
            if pidPath.exists():
                with Path.open(pidPath, "r") as f:
                    read_data = f.readline()
                    f.close()
                
                read_pid, read_proc, stdIN, stdOUT, stdERR = read_data.split("|")

                read_pid = int(read_pid)

                stdIN = Path(stdIN)
                stdOUT = Path(stdOUT)
                stdERR = Path(stdERR)

                if psutil.pid_exists(read_pid):
                    p = psutil.Process(read_pid)
                    if f"{p.cmdline()}".find(f'$host.ui.RawUI.WindowTitle = "{process_name}"') != -1 and read_proc == process_name:
                        return "Pid is Unchanged", 1, stdIN, stdOUT, stdERR
                    else:
                        Path.unlink(pidPath)
                        return "Process was not the same as memory, forgetting...", 4, stdIN, stdOUT, stdERR
                else:
                    Path.unlink(pidPath)
                    return "Pid does not exist, forgetting...", 2, stdIN, stdOUT, stdERR
            else:
                return "Pid is not memorized", 3, Path(""), Path(""), Path("")
        else:
            return "Root directory for pids has not been set", 0, Path(""), Path(""), Path("")
    
    def RemoveMemory(self, pidPath: Path):
        if pidPath.exists():
            pidPath.unlink()

"""
--GetMemory Returns--
0: "Root directory for pids has not been set"
1: "Pid is Unchanged"
2: "Pid does not exist, forgetting..."
3: "Pid is not memorized"
4: "Process was not the same as memory, forgetting..."

--Memorize Returns--
0: "Root directory for pids has not been set"
1: "Process has been memorized"
2: "Pid is already in memory"
"""