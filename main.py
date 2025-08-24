import psutil, subprocess, time, socket, uuid, os
from pathlib import Path
from flask import Flask, Response, request
from mem import Memorization

app = Flask(__name__)
# socketIo = SocketIO(app)

serverName = "GTNH Server"
# serverStartCMD = 'D:\\MinecraftServers\\Modded\\GregTech_New_Horizons\\GT_New_Horizons_2.7.4_Server_Java_17-21\\startserver-java9.bat'
# serverStartARGS = ['C:\\WINDOWS\\system32\\cmd.exe', '/c', 'D:\\MinecraftServers\\Modded\\GregTech_New_Horizons\\GT_New_Horizons_2.7.4_Server_Java_17-21\\startserver-java9.bat']
# serverStartCMD = r'C:\\WINDOWS\\system32\\cmd.exe'
# serverStartARGS = '/c', 'D:\\MinecraftServers\\Modded\\GregTech_New_Horizons\\GT_New_Horizons_2.7.4_Server_Java_17-21\\startserver-java9.bat'
serverJava_exe = "C:/Program Files/Microsoft/jdk-11.0.16.101-hotspot/bin/java.exe"
serverArgs = ["-Xms6G", "-Xmx6G", "-Dfml.readTimeout=180", "@java9args.txt", "-jar", "lwjgl3ify-forgePatches.jar", "nogui"]
serverCwd = "D:/MinecraftServers/Modded/GregTech_New_Horizons/GT_New_Horizons_2.7.4_Server_Java_17-21"

playitggStartCMD = "C:\\Users\\lindg\\Apps\\playit_gg\\bin\\playit.exe"
playitggStartCWD = "C:\\Users\\lindg\\Apps\\playit_gg\\bin"

serverPID = -1
playit_gg_PID = -1

mem = Memorization(Path("knownPids"))
# print(mem.Memorize(25575, "java.exe"))
# print(mem.GetMemory(25575, "ja34.exe"))

# Double check that the server pids was still valid (not changed)
if Path("knownPids").exists():
    checkedPaths = []

    worked = False
    for knownPid in Path("knownPids").iterdir():
        pid, name, _, _, _ = Path.read_text(Path(knownPid)).split("|")
        pid = int(pid)
        if name == serverName or name == "Playit.gg":
            # mem.readMode = "normal"
            string_res, nr_res, stdIN, stdOUT, stdERR = mem.GetMemory(pid, name)
            # mem.readMode = "text"
            # string_res = mem.GetMemory(pid, name)
            if nr_res == 1:
                if name == serverName:
                    serverPID = pid
                elif name == "Playit.gg":
                    playit_gg_PID = pid

                if stdIN.exists():
                    checkedPaths.append(stdIN)

                if stdOUT.exists():
                    checkedPaths.append(stdOUT)

                if stdERR.exists():
                    checkedPaths.append(stdERR)

                worked = True

            if nr_res == 2 or nr_res == 4:
                pidInPath = Path(stdIN)
                pidOutPath = Path(stdOUT)
                pidErrPath = Path(stdERR)
                
                if pidOutPath.exists():
                    pidOutPath.unlink()

                if pidInPath.exists():
                    pidOutPath.unlink()

                if pidErrPath.exists():
                    pidOutPath.unlink()
            
            print(f"File: {knownPid} had memory result: {string_res}")
        
    for path in Path("ProcessOutIn").iterdir():
        if path not in checkedPaths:
            path.unlink()
    
    if not worked:
        print("There was no pids to double check")

    # mem.readMode = "text"
    if serverPID == -1 or playit_gg_PID == -1:
        if serverPID == -1:
            print(f"Checking if server is running under name: {serverName}")

        if playit_gg_PID == -1:
            print(f"Checking if playit is running under name: Playit.gg")

        for pid in psutil.pids():
            # print(f"Checking pid: {pid}")
            try:
                p = psutil.Process(pid)
                # print(p.cmdline())

                if serverPID == -1:
                    if f"{p.cmdline()}".find(f'$host.ui.RawUI.WindowTitle = "{serverName}"') != -1:
                        serverPID = pid
                        
                        name = p.cmdline()[1].split(";")[1].replace(" $host.ui.RawUI.WindowTitle = ", "")[1:-1]
                        print(mem.Memorize(pid, name))

                if playit_gg_PID == -1:
                    if f"{p.cmdline()}".find('$host.ui.RawUI.WindowTitle = "Playit.gg"') != -1:
                        playit_gg_PID = pid

                        name = p.cmdline()[1].split(";")[1].replace(" $host.ui.RawUI.WindowTitle = ", "")[1:-1]
                        print(mem.Memorize(pid, name))

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                pass

        if serverPID == -1:
            print(f"{serverName} could be found under name: {serverName}")

        if playit_gg_PID == -1:
            print(f"Playit could not be found under name: Playit.gg")

def check_port_active(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    res = sock.connect_ex(('localhost', port))
    sock.close()
    return res == 0

@app.errorhandler(Exception)
def internal_error(error):
    return f"[INTERNAL ERROR]:  {error}"

@app.errorhandler(404)
def not_found(error):
    return "Excuse me, this page does not exist!"

# async def applicationRunning(name: str, recursive: bool = False):
async def applicationRunning(pid: int):
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
            return True
    
    return False

async def serverOn(asText: bool = False):
    if await applicationRunning(serverPID):
        if asText:
            return "On"
        else:
            return True
    if asText:
        return "Off"
    else:
        return False

@app.route('/awake')
def awake():
    global serverIsOn
    # serverIsOn = not serverIsOn
    resp = Response()
    if serverOn():
        resp.status = 200
    else:
        resp.status = 503
        
    # print("Received /start request")
    # return "Server started successfully!"
    return resp

@app.route('/sendMessage', methods=["POST", "GET"])
def sendMessage():
    if request.method == "POST":
        resp = Response()
        resp.status = 200
        resp.set_data("Recieved")

        print(request.data)

        return resp

    elif request.method == "GET":
        return "HELLO"
    
    return ""

@app.route('/start')
async def startServer():
    global serverPID, playit_gg_PID

    print('Received "/start" request')

    # if not await serverOn() or not await applicationRunning("Playit.gg"):
    if not await serverOn() or not await applicationRunning(playit_gg_PID):
        try:
            if not await serverOn():
                print("Starting server...")

                # exec(serverStartFile)
                # subprocess.call([serverStartFile])
                # os.startfile(serverStartFile)
                # subprocess.Popen(serverStartCMD, cwd=serverStartCWD, shell=True)
                # os.system(serverStartCMD)
                # os.spawnl(os.P_DETACH, serverStartCMD, serverStartCWD)#, serverStartARGS[0], serverStartARGS[1], serverStartARGS[2])

                # flags = (
                #     subprocess.DETACHED_PROCESS
                #     | subprocess.CREATE_NEW_PROCESS_GROUP
                #     | subprocess.CREATE_NEW_CONSOLE
                # )
                flags = (
                    subprocess.CREATE_BREAKAWAY_FROM_JOB
                    | subprocess.CREATE_NEW_PROCESS_GROUP
                    | subprocess.CREATE_NEW_CONSOLE
                )

                # command = f'title {serverName} && "{serverJava_exe}" {" ".join(serverArgs)}'
                # command = ['powershell.exe', '-NoExit', f'cd "{serverCwd}"; $host.ui.RawUI.WindowTitle = "{serverName}"; & cmd /c "{serverJava_exe}" {" ".join(serverArgs)}']
                cmd = "& cmd /c '\"C:\\Program Files\\Microsoft\\jdk-11.0.16.101-hotspot\\bin\\java.exe\" -Xms6G -Xmx6G -Dfml.readTimeout=180 @java9args.txt -jar lwjgl3ify-forgePatches.jar nogui'"
                command = ['powershell.exe', f'cd "{serverCwd}"; $host.ui.RawUI.WindowTitle = "{serverName}"; {cmd}']
                
                # Create temporary uuid for file
                tmpUUID = uuid.uuid4()
                stdinPath = Path(f"ProcessOutIn/{tmpUUID}_input.txt")
                stdoutPath = Path(f"ProcessOutIn/{tmpUUID}_output.txt")
                stderrPath = Path(f"ProcessOutIn/{tmpUUID}_err.txt")

                # Create temporary files
                Path.touch(stdinPath)
                Path.touch(stdoutPath)
                Path.touch(stderrPath)

                # Set files and launch process
                with open(stdinPath, "r") as f_in, open(stdoutPath, "w") as f_out, open(stderrPath, "w") as f_err:
                    proc = subprocess.Popen(command, stdin=f_in, stdout=f_out, stderr=f_err, cwd=serverCwd, creationflags=flags, close_fds=True)
                    f_in.close()
                    f_out.close()
                    f_err.close()
                
                if psutil.pid_exists(proc.pid):
                    p = psutil.Process(proc.pid)
                    serverPID = p.pid

                    name = command[1].split(";")[1].replace(" $host.ui.RawUI.WindowTitle = ", "")[1:-1]
                    mem.Memorize(p.pid, name, stdinPath, stdoutPath, stderrPath)

                    print(f"GTNH Server pid: {p.pid}")

                    print("Started server")
            
            # if not await applicationRunning("Playit.gg"):
            if not await applicationRunning(playit_gg_PID):
                print("Starting playit.gg...")
                # exec(startPlayitGGFile)
                # subprocess.call([PlayitGGStartFile])
                # os.startfile(playitggStartFile)
                # subprocess.Popen(playitggStartCMD, cwd=playitggStartCWD, shell=True, )
                # os.system(playitggStartCMD)

                flags = (
                    subprocess.CREATE_BREAKAWAY_FROM_JOB
                    | subprocess.CREATE_NEW_PROCESS_GROUP
                    | subprocess.CREATE_NEW_CONSOLE
                )

                # command = f'title {serverName} && "{playitggStartCMD}"'
                # command = ['cmd.exe', '/C', f'title Playit.gg && "{playitggStartCMD}"']
                # command = ['cmd.exe', '/K', f'cd "{playitggStartCWD}" && title Playit.gg && "{playitggStartCMD}"']
                command = ['powershell.exe', f'cd "{playitggStartCWD}"; $host.ui.RawUI.WindowTitle = "Playit.gg"; & "{playitggStartCMD}"']
                # print(command)

                # Create temporary uuid for file
                tmpUUID = uuid.uuid4()
                stdinPath = Path(f"PrecessOutIn/{tmpUUID}_input.txt")
                stdoutPath = Path(f"PrecessOutIn/{tmpUUID}_output.txt")
                stderrPath = Path(f"PrecessOutIn/{tmpUUID}_err.txt")

                # Create temporary files
                Path.touch(stdinPath)
                Path.touch(stdoutPath)
                Path.touch(stderrPath)

                with open(stdinPath, "r") as f_in, open(stdoutPath, "w") as f_out, open(stderrPath, "w") as f_err:
                    proc = subprocess.Popen(command, stdin=f_in, stdout=f_out, stderr=f_err, cwd=playitggStartCWD, creationflags=flags, close_fds=True)
                    f_in.close()
                    f_out.close()
                    f_err.close()

                if psutil.pid_exists(proc.pid):
                    p = psutil.Process(proc.pid)
                    playit_gg_PID = p.pid
                    
                    name = command[1].split(";")[1].replace(" $host.ui.RawUI.WindowTitle = ", "")[1:-1]
                    mem.Memorize(p.pid, name, stdinPath, stdoutPath, stderrPath)

                    print(f"Playig.gg pid: {p.pid}")

                    print("Started playit.gg")

            for n in range(10 +1):
                n = 10-n
                if n <= 0:
                    return f"Server could not be started or took more than 10 seconds"
                string = f"Waiting for server ping, {n}"
                print(string)
                # emit('Waiting for server ping', {'n': f'{10-n}'}, broadcast=True)
                # return f"Waiting for server ping, {10-n}"
                time.sleep(1)
                if await serverOn():
                    break

            for n in range(10 +1):
                n = 10-n
                if n <= 0:
                    return f"Playit.gg could not be started or took more than 10 seconds"
                string = f"Waiting for playit ping, {n}"
                print(string)
                # emit('Waiting for playit ping', {'n': f'{10-n}'}, broadcast=True)
                # return f"Waiting for playit ping, {10-n}"
                time.sleep(1)
                # if await applicationRunning("Playit.gg"):
                if await applicationRunning(playit_gg_PID):
                    break
                    
            # if await serverOn() and await applicationRunning("Playit.gg"):
            if await serverOn() and await applicationRunning(playit_gg_PID):
                return f"Server and playit.gg started succesfully"
            else:
                return f"Server or playit.gg could not start, unknown cause"

        except OSError as e:
            raise Exception(f"Server error catched... Aborting!   Error was: {e}")
            
    else:
        return "Server is already on"

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
    # for pid_raw in psutil.pids():
    #     # pid = pid_raw.pid
    #     pid = pid_raw
    #     try:
    #         if psutil.pid_exists(pid):
    #             p = psutil.Process(pid)

    #             PrintSafeProcess(p)
    #     except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
    #         # print(e)
    #         pass

    #     print()

    # print(applicationRunning("Playit.gg"))
    
    app.run(host='0.0.0.0', port=8080)

    while True:
        if serverPID != -1:
            pass

    # socketIo.run(app, host='0.0.0.0', port=8080, debug=True)
    pass
