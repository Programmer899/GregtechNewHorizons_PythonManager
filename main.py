import psutil, subprocess, time, os, uuid
from pathlib import Path
from flask import Flask, Response, render_template, request

# Own modules
from mem import Memorization
from checkIfServerRunning import check_port
from ShutdownServer import ShutdownServer
from pingMinecraftServer import ServerPingResponse, ServerPing

app = Flask(__name__)

# serverStartCMD = 'D:\\MinecraftServers\\Modded\\GregTech_New_Horizons\\GT_New_Horizons_2.7.4_Server_Java_17-21\\startserver-java9.bat'
# serverStartARGS = ['C:\\WINDOWS\\system32\\cmd.exe', '/c', 'D:\\MinecraftServers\\Modded\\GregTech_New_Horizons\\GT_New_Horizons_2.7.4_Server_Java_17-21\\startserver-java9.bat']
# serverStartCMD = r'C:\\WINDOWS\\system32\\cmd.exe'
# serverStartARGS = '/c', 'D:\\MinecraftServers\\Modded\\GregTech_New_Horizons\\GT_New_Horizons_2.7.4_Server_Java_17-21\\startserver-java9.bat'
serverJava_exe = "C:/Program Files/Microsoft/jdk-11.0.16.101-hotspot/bin/java.exe"
serverArgs = ["-Xms6G", "-Xmx6G", "-Dfml.readTimeout=180", "@java9args.txt", "-jar", "lwjgl3ify-forgePatches.jar", "nogui"]
serverCwd = "D:/MinecraftServers/Modded/GregTech_New_Horizons/GT_New_Horizons_2.7.4_Server_Java_17-21"

playitggStartCMD = "C:\\Users\\lindg\\Apps\\playit_gg\\bin\\playit.exe"
playitggStartCWD = "C:\\Users\\lindg\\Apps\\playit_gg\\bin"

serverName = "GTNH Server"
playitName = "Playit.gg"

serverPID = -1
playit_gg_PID = -1

serverPing = ServerPing("127.0.0.1", 25575)
serverStartMode = False

everythingOn = True

# Double check that the server pids was still valid (not changed)
knownPidsPath = Path("knownPids")
processOutInPath = Path("processOutIn")
mem = Memorization(knownPidsPath)

if knownPidsPath.exists():
    if processOutInPath.exists():
        checkedPaths = []

        worked = False
        for knownPid in knownPidsPath.iterdir():
            pid, name, _, _, _ = Path.read_text(Path(knownPid)).split("|")
            pid = int(pid)
            if name == serverName or name == playitName:
                # mem.readMode = "normal"
                string_res, nr_res, stdIN, stdOUT, stdERR = mem.GetMemory(pid, name)
                # mem.readMode = "text"
                # string_res = mem.GetMemory(pid, name)
                if nr_res == 1:
                    if name == serverName:
                        serverPID = pid
                        
                    elif name == playitName:
                        playit_gg_PID = pid

                    if stdIN.exists() and (stdIN != "." and stdIN != ".."):
                        checkedPaths.append(stdIN)

                    if stdOUT.exists() and (stdOUT != "." and stdOUT != ".."):
                        checkedPaths.append(stdOUT)

                    if stdERR.exists() and (stdERR != "." and stdERR != ".."):
                        checkedPaths.append(stdERR)

                    worked = True

                if nr_res == 2 or nr_res == 4:
                    pidInPath = Path(stdIN)
                    pidOutPath = Path(stdOUT)
                    pidErrPath = Path(stdERR)
                    
                    if pidInPath.exists() and pidInPath != "." and pidInPath != "..":
                        print(f"{pidInPath} was found in {name}")
                        # pidInPath.unlink()

                    if pidOutPath.exists() and pidOutPath != "." and pidOutPath != "..":
                        print(f"{pidOutPath} was found in {name}")
                        # pidOutPath.unlink()

                    if pidErrPath.exists() and pidErrPath != "." and pidErrPath != "..":
                        print(f"{pidErrPath} was found in {name}")
                        # pidErrPath.unlink()

                print(f"File: {knownPid} had memory result: {string_res}")
            
        for path in processOutInPath.iterdir():
            if path not in checkedPaths:
                path.unlink()
        
        if not worked:
            print("There was no pids to double check")

        # mem.readMode = "text"
        if serverPID == -1 or playit_gg_PID == -1:
            if serverPID == -1:
                print(f"Checking if server is running under name: {serverName}")

            if playit_gg_PID == -1:
                print(f"Checking if playit is running under name: {playitName}")

            for pid in psutil.pids():
                # print(f"Checking pid: {pid}")
                try:
                    p = psutil.Process(pid)
                    # print(p.cmdline())

                    if serverPID == -1:
                        if f"{p.cmdline()}".find("GT_New_Horizons_2.7.4_Server_Java_17-21") != -1:
                            serverPID = pid
                            
                            print(mem.Memorize(pid, serverName))
                            
                    if playit_gg_PID == -1:
                        if f"{p.cmdline()}".find(f'$host.ui.RawUI.WindowTitle = "{playitName}"') != -1:
                            playit_gg_PID = pid

                            name = p.cmdline()[1].split(";")[1].replace(" $host.ui.RawUI.WindowTitle = ", "")[1:-1]
                            print(mem.Memorize(pid, playitName))

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    pass

            if serverPID == -1:
                print(f"{serverName} could be found under name: {serverName}")

            if playit_gg_PID == -1:
                print(f"Playit could not be found under name: {playitName}")
    else:
        print(f"Warning, server run at own risk. {processOutInPath} not found")
else:
    print(f"Warning, server run at own risk. {knownPidsPath} not found")

@app.errorhandler(Exception)
def internal_error(error):
    return f"[INTERNAL ERROR]:  {error}"

@app.errorhandler(404)
def not_found(error):
    return "Excuse me, this page does not exist!"

async def applicationRunning(pid: int, playit: bool = False, gtnh: bool = False):
    global playit_gg_PID, serverPID
        
    if pid == -1:
        return False

    if psutil.pid_exists(pid):
        p = psutil.Process(pid)

        if p.is_running():
            return True
    
    if playit:
        playit_gg_PID = -1

    if gtnh:
        serverPID = -1

    return False

async def serverOn(asText: bool = False):
    # if await applicationRunning(serverPID):
    if await check_port(25575):
        if asText:
            return "On"
        else:
            return True
    if asText:
        return "Off"
    else:
        return False

@app.route('/awake/Playit')
async def awakePlayit():
    # serverIsOn = not serverIsOn
    resp = Response()
    if await applicationRunning(playit_gg_PID, playit=True):
        resp.status = 200
    else:
        resp.status = 503
        
    # print("Received /start request")
    # return "Server started successfully!"
    return resp

@app.route('/awake/GTNH')
async def awakeGTNH():
    # serverIsOn = not serverIsOn
    resp = Response()
    data = serverPing.Ping()

    if data != None:
        if not data.isEmpty():
            resp.status = 200
        else:
            resp.status = 503
    else:
        resp.status = 503
        
    # print("Received /start request")
    # return "Server started successfully!"
    return resp

@app.route('/awake/All')
async def awake():
    # serverIsOn = not serverIsOn
    resp = Response()
    data = serverPing.Ping()

    if data != None:
        if not data.isEmpty() and await applicationRunning(playit_gg_PID, playit=True):
            resp.status = 200
        else:
            resp.status = 503
    else:
        resp.status = 503
        
    # print("Received /start request")
    # return "Server started successfully!"
    return resp

@app.route('/starting')
async def starting():
    global serverStartMode
    resp = Response()
    data = serverPing.Ping()
    if serverStartMode and not await serverOn() and data == None:
        resp.status = 200
    else:
        resp.status = 503
        
    # print("Received /start request")
    # return "Server started successfully!"
    return resp

# @app.route('/sendMessage', methods=["POST", "GET"])
# def sendMessage():
#     if request.method == "POST":
#         resp = Response()
#         resp.status = 200
#         resp.set_data("Recieved")

#         print(request.data)

#         return resp

#     elif request.method == "GET":
#         return "HELLO"
    
#     return ""

@app.route('/computerTurnOff')
async def computerTurnOff():
    global playit_gg_PID

    playitRunning = False

    if psutil.pid_exists(playit_gg_PID):
        p = psutil.Process(playit_gg_PID)

        if p.is_running():
            playitRunning = True
    
    if not playitRunning and not await serverOn() and not check_port(25575):
        subprocess.run(["shutdown", "-s"])

        return "Computer is now turning off"

    return "Computer could not be turned off"

@app.route('/stop')
async def stopServer():
    if await serverOn() or check_port(25575):
        resp = await ShutdownServer()
        
        if psutil.pid_exists(playit_gg_PID):
            p = psutil.Process(playit_gg_PID)
            if p.is_running():
                p.kill()

        return f"{resp}"
        # return "Server has now been closed"
    else:
        return "Server is already closed"

@app.route('/start')
async def startServer():
    global serverPID, playit_gg_PID, serverStartMode

    print('Received "/start" request')

    # if not await serverOn() or not await applicationRunning("Playit.gg"):
    if not await serverOn() or not await applicationRunning(playit_gg_PID, playit=True):
        try:
            if not await serverOn():
                print("Starting server...")
                serverStartMode = True

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
                stdinPath  = Path(f"{processOutInPath}/{tmpUUID}_GTNH_input.txt")
                stdoutPath = Path(f"{processOutInPath}/{tmpUUID}_GTNH_output.txt")
                stderrPath = Path(f"{processOutInPath}/{tmpUUID}_GTNH_err.txt")

                # Create temporary files
                stdinPath.touch()
                stdoutPath.touch()
                stderrPath.touch()

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
            if not await applicationRunning(playit_gg_PID, playit=True):
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
                command = ['powershell.exe', f'cd "{playitggStartCWD}"; $host.ui.RawUI.WindowTitle = "{playitName}"; & "{playitggStartCMD}"']
                # print(command)

                # Create temporary uuid for file
                tmpUUID = uuid.uuid4()
                stdinPath  = Path(f"{processOutInPath}/{tmpUUID}_PlayitGG_input.txt")
                stdoutPath = Path(f"{processOutInPath}/{tmpUUID}_PlayitGG_output.txt")
                stderrPath = Path(f"{processOutInPath}/{tmpUUID}_PlayitGG_err.txt")

                # Create temporary files
                stdinPath.touch()
                stdoutPath.touch()
                stderrPath.touch()

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
                if await applicationRunning(playit_gg_PID, playit=True):
                    break
            
            # if await serverOn() and await applicationRunning("Playit.gg"):
            if await serverOn() and await applicationRunning(playit_gg_PID, playit=True):
                return f"Server and playit.gg started succesfully"
            else:
                serverStartMode = False
                return f"Server or playit.gg could not start, unknown cause"

        except OSError as e:
            print(OSError(f"Server error catched... Aborting!   Error was: {e}"))
            serverStartMode = False
            raise Exception(f"Server error catched... Aborting!   Error was: {e}")
            
    else:
        # return "Server is already on"
        return Home()

@app.route('/')
def Home():
    return render_template("MainPage.html")

def updatePids():
    global serverPID, playit_gg_PID

    checkedPaths = []

    worked = False
    for knownPid in knownPidsPath.iterdir():
        pid, name, _, _, _ = Path.read_text(Path(knownPid)).split("|")
        pid = int(pid)
        if name == serverName or name == playitName:
            string_res, nr_res, stdIN, stdOUT, stdERR = mem.GetMemory(pid, name)
            if nr_res == 1:
                if name == serverName:
                    serverPID = pid
                    
                elif name == playitName:
                    playit_gg_PID = pid

                if stdIN.exists() and (stdIN != "." and stdIN != ".."):
                    checkedPaths.append(stdIN)

                if stdOUT.exists() and (stdOUT != "." and stdOUT != ".."):
                    checkedPaths.append(stdOUT)

                if stdERR.exists() and (stdERR != "." and stdERR != ".."):
                    checkedPaths.append(stdERR)

                worked = True

            if nr_res == 2 or nr_res == 4:
                pidInPath = Path(stdIN)
                pidOutPath = Path(stdOUT)
                pidErrPath = Path(stdERR)
                
                if pidInPath.exists() and pidInPath != "." and pidInPath != "..":
                    pidInPath.unlink()

                if pidOutPath.exists() and pidOutPath != "." and pidOutPath != "..":
                    pidOutPath.unlink()

                if pidErrPath.exists() and pidErrPath != "." and pidErrPath != "..":
                    pidErrPath.unlink()

            print(f"File: {knownPid} had memory result: {string_res}")
        
    for path in processOutInPath.iterdir():
        if path not in checkedPaths:
            if path.exists():
                path.unlink()
    
    if not worked:
        print("There was no pids to double check")

    # mem.readMode = "text"
    if serverPID == -1 or playit_gg_PID == -1:
        for pid in psutil.pids():
            try:
                p = psutil.Process(pid)

                if serverPID == -1:
                    if f"{p.cmdline()}".find("GT_New_Horizons_2.7.4_Server_Java_17-21") != -1:
                        serverPID = pid
                        
                        print(mem.Memorize(pid, serverName))
                        
                if playit_gg_PID == -1:
                    if f"{p.cmdline()}".find(f'$host.ui.RawUI.WindowTitle = "{playitName}"') != -1:
                        playit_gg_PID = pid

                        name = p.cmdline()[1].split(";")[1].replace(" $host.ui.RawUI.WindowTitle = ", "")[1:-1]
                        print(mem.Memorize(pid, playitName))

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

    while everythingOn:
        updatePids()
    
    print(f"Everything has now been closed")
