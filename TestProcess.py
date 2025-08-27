import psutil

# async def applicationRunning(name: str, recursive: bool = False):
async def applicationRunning(pid: int, raw: bool):
    # if recursive:
    #     output = subprocess.check_output(
    #         f'tasklist /v /fo csv /fi "imagename eq {name}"', shell=True, text=True
    #     ).split("\n")
    # else:
    #     output = subprocess.check_output(
    #         f'tasklist /v /fo csv /fi "imagename eq WindowsTerminal.exe"', shell=True, text=True
    #     ).split("\n")

    # output.pop(0)

    # recursiveList = []

    # if output:
    #     for line in output:
    #         if name in line:
    #             print(line)
    #             window = line.split(",")[-1]
    #             # print(window)
    #             if recursive:
    #                 recursiveList.append(window)
    #             else:
    #                 return True
    #             # recursiveList.append(window.split("\\")[-1])
        
    #     if recursive:
    #         return recursiveList

    # return False

    if pid == -1:
        return False

    if psutil.pid_exists(pid):
        p = psutil.Process(pid)

        if p.is_running():
            if raw:
                return p
            else:
                return True
    
    return False

def PrintSafeProcess(process: psutil.Process):
    try:
        print(f"Pid: {process.pid}")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        pass
    try:
        print(f"Name: {process.name()}")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        pass
    try:
        print(f"Username: {process.username()}")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        pass
    try:
        print(f"Exe path: {process.exe()}")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        pass
    try:
        print(f"Working directory: {process.cwd()}")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        pass
    # try:
    #     print(f"Children:\n{process.children(True)}")
    # except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
    #     pass
    try:
        print(f"Cmdline called: {process.cmdline()}")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        pass

if __name__ == '__main__':
    for pid_raw in psutil.pids():
        # pid = pid_raw.pid
        pid = pid_raw
        try:
            if psutil.pid_exists(pid):
                p = psutil.Process(pid)

                PrintSafeProcess(p)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            # print(e)
            pass

        print()

    # print(applicationRunning("Playit.gg"))