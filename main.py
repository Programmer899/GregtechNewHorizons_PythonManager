import psutil, subprocess, time, os, uuid, signal, threading
from pathlib import Path
from flask import Flask, Response, render_template, request

# Own modules
from Helpers.mem import Memorization
from Helpers.checkIfServerRunning import check_port
from Helpers.ShutdownServer import ShutdownServer
from Helpers.pingMinecraftServer import ServerPingResponse, ServerPing
from Helpers.findApplication import findApplication
from Helpers.controlled import WhileFunctionWithStop, ControlledThread
from Helpers.repeatedFunction import RepeatedFunction

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
playitCliName = "playit"

serverPID = -1
playit_gg_PID = -1
playitCli_PID = -1

# Running processes for easier use
serverProcess = None
playitProcess = None
playitCliProcess = None

stopUpdateThread = False

serverPing = ServerPing("127.0.0.1", 25575)
serverStartMode = False

everythingOn = True

# Double check that the server pids was still valid (not changed)
knownPidsPath = Path("knownPids")
processOutInPath = Path("processOutIn")
mem = Memorization(knownPidsPath)

with open("WebService\\service.log", "w") as f:
    f.write("")
    f.close()

if knownPidsPath.exists():
    if processOutInPath.exists():
        checkedPaths = []

        worked = False
        for knownPid in knownPidsPath.iterdir():
            pid, name, _, _, _ = Path.read_text(Path(knownPid)).split("|")
            pid = int(pid)
            if name == serverName or name == playitName or name == playitCliName:
                # mem.readMode = "normal"
                string_res, nr_res, stdIN, stdOUT, stdERR = mem.GetMemory(pid, name)
                # mem.readMode = "text"
                # string_res = mem.GetMemory(pid, name)
                if nr_res == 1:
                    if name == serverName:
                        serverPID = pid
                        serverProcess = psutil.Process(pid)
                        
                    elif name == playitName:
                        playit_gg_PID = pid
                        playitProcess = psutil.Process(pid)

                    elif name == playitCliName:
                        playitCli_PID = pid
                        playitCliProcess = psutil.Process(pid)

                    if stdIN.exists() and (stdIN != "." and stdIN != ".."):
                        checkedPaths.append(stdIN)

                    if stdOUT.exists() and (stdOUT != "." and stdOUT != ".."):
                        checkedPaths.append(stdOUT)

                    if stdERR.exists() and (stdERR != "." and stdERR != ".."):
                        checkedPaths.append(stdERR)

                    worked = True

                if nr_res == 2 or nr_res == 4:
                    if name == serverName:
                        serverProcess = None
                        
                    elif name == playitName:
                        playitProcess = None

                    elif name == playitCliName:
                        playitCliProcess = None

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
        if serverPID == -1 or playit_gg_PID == -1 or playitCli_PID == -1:
            if serverPID == -1:
                print(f"Checking if server is running under name: {serverName}")

            if playit_gg_PID == -1:
                print(f"Checking if playit is running under name: {playitName}")

            if playitCli_PID == -1:
                print(f"Checking if playit-cli is running under name: {playitName}")

            try:
                # p = psutil.Process(pid)

                # if serverPID == -1:
                #     if f"{p.cmdline()}".find("GT_New_Horizons_2.7.4_Server_Java_17-21") != -1:
                #         serverPID = pid
                        
                #         print(mem.Memorize(pid, serverName))

                p = findApplication("CommandLine", "GT_New_Horizons_2.7.4_Server_Java_17-21")

                if p != None:
                    serverPID = p.pid
                    serverProcess = psutil.Process(p.pid)
                    
                    print(mem.Memorize(p.pid, serverName))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                pass

            try:
                # if playit_gg_PID == -1:
                #     if f"{p.cmdline()}".find(f'$host.ui.RawUI.WindowTitle = "{playitName}"') != -1:
                #         playit_gg_PID = pid

                #         name = p.cmdline()[1].split(";")[1].replace(" $host.ui.RawUI.WindowTitle = ", "")[1:-1]
                #         print(mem.Memorize(pid, playitName))

                p = findApplication("CommandLine", f"{playitName}")

                if p != None:
                    playit_gg_PID = p.pid
                    playitProcess = psutil.Process(p.pid)
                    
                    print(mem.Memorize(p.pid, playitName))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                pass

            try:
                p = findApplication("NameUnsafe", playitCliName)

                if p != None:
                    playitCli_PID = p.pid
                    playitCliProcess = psutil.Process(p.pid)
                    
                    print(mem.Memorize(p.pid, playitCliName))    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                pass            
                        
            if serverPID == -1:
                print(f"{serverName} could be found under name: {serverName}")

            if playit_gg_PID == -1:
                print(f"Playit could not be found under name: {playitName}")

            if playitCli_PID == -1:
                print(f"Playit-Cli could not be found under name: {playitCliName}")
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
    resp = Response()

    # if await applicationRunning(playit_gg_PID, playit=True):
    # if playitProcess != None and playitCliProcess != None:
    if playitCliProcess != None:
        # if not data.isEmpty() and await applicationRunning(playit_gg_PID, playit=True):
        # if playitProcess.is_running() or playitCliProcess.is_running():
        if playitCliProcess.is_running():
            resp.status = 200
        else:
            resp.status = 503
    else:
        resp.status = 503
        
    # print("Received /start request")
    # return "Server started successfully!"
    return resp

@app.route('/awake/GTNH')
async def awakeGTNH():
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
    resp = Response()
    resp.status = 503 # Make ready for error

    data = serverPing.Ping()

    # if data != None and playitProcess != None and playitCliProcess != None:
    #     # if not data.isEmpty() and await applicationRunning(playit_gg_PID, playit=True):
    #     if not data.isEmpty() or (playitProcess.is_running() and playitCliProcess.is_running()):
    #         resp.status = 200
    #     else:
    #         resp.status = 503
    # else:
    #     resp.status = 503

    if data != None:
        if not data.isEmpty():
            resp.status = 200

    # if playitProcess != None and playitCliProcess != None:
    #     if (playitProcess.is_running() and playitCliProcess.is_running()):
    #         resp.status = 200
    if playitCliProcess != None:
        if playitCliProcess.is_running():
            resp.status = 200

    # print("Received /start request")
    # return "Server started successfully!"
    return resp

@app.route('/starting')
async def starting():
    global serverStartMode
    resp = Response()
    data = serverPing.Ping()
    if serverStartMode and data == None:
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
    global everythingOn
    global playit_gg_PID

    playitNotRunning = True
    playitCliNotRunning = True
    serverNotRunning = True

    if psutil.pid_exists(serverPID):
        try:
            p = psutil.Process(serverPID)

            if p.is_running():
                serverNotRunning = False
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        
    if psutil.pid_exists(playit_gg_PID):
        try:
            p = psutil.Process(playit_gg_PID)

            if p.is_running():
                playitNotRunning = False
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if psutil.pid_exists(playitCli_PID):
        try:
            p = psutil.Process(playitCli_PID)

            if p.is_running():
                playitCliNotRunning = False
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if serverNotRunning and playitNotRunning and playitCliNotRunning and not await check_port(25575):
        everythingOn = False
        subprocess.run(["shutdown", "-s", "-t", "5"])

        return "Computer is now turning off"

    return "Computer could not be turned off, server or playit is still on"

@app.route('/computerFORCEOff')
async def computerFORCEOff():
    global everythingOn

    ShutdownServer()
    everythingOn = False

    time.sleep(3)

    try:
        if psutil.pid_exists(serverPID):
            p = psutil.Process(serverPID)
            if p.is_running():
                p.kill()

        if psutil.pid_exists(playit_gg_PID):
            p = psutil.Process(playit_gg_PID)
            if p.is_running():
                p.kill()

        if psutil.pid_exists(playitCli_PID):
            p = psutil.Process(playitCli_PID)
            if p.is_running():
                p.kill()
    except OSError:
        pass

    subprocess.run(["shutdown", "-s", "-t", "0"])

    return "Computer was forced to shut down"

@app.route('/stop')
async def stopServer():
    resp = Response()
    data = "Minecraft server was not closed |"

    if await serverOn() or check_port(25575):
        resp = ShutdownServer()
        
    if psutil.pid_exists(playit_gg_PID):
        p = psutil.Process(playit_gg_PID)
        if p.is_running():
            os.kill(p.pid, signal.SIGINT)
            # p.kill()
            data.join(" Playit has been closed |")

    if psutil.pid_exists(playitCli_PID):
        p = psutil.Process(playitCli_PID)
        if p.is_running():
            # p.kill()
            os.kill(p.pid, signal.SIGINT)
            data.join(" PlayitCli has been closed |")
    
    resp.data = data

    # if (not await serverOn() and not check_port(25575)) and (findApplication("PID", f"{playit_gg_PID}") == None and findApplication("PID", f"{playitCli_PID}") == None):
    if (not await serverOn() and not check_port(25575)) and findApplication("PID", f"{playitCli_PID}") == None:
        return f"{resp.data}"
    else:
        return "Server is already closed"

@app.route('/closeWebsite')
async def CloseWebsite():
    resp = Response()
    resp.data = "Server has been closed"
    try:
        os.kill(os.getpid(), signal.SIGINT)

        resp.status = 200

        return resp
        # return "Server has now been closed"
    except OSError:
        resp.status = 503
        resp.data = "Website could not be closed"

    return resp

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

            # for n in range(10 +1):
            #     n = 10-n
            #     if n <= 0:
            #         return f"Server could not be started or took more than 10 seconds"
            #     string = f"Waiting for server ping, {n}"
            #     print(string)
            #     # emit('Waiting for server ping', {'n': f'{10-n}'}, broadcast=True)
            #     # return f"Waiting for server ping, {10-n}"
            #     time.sleep(1)
            #     if await serverOn():
            #         break

            # for n in range(10 +1):
            #     n = 10-n
            #     if n <= 0:
            #         return f"Playit.gg could not be started or took more than 10 seconds"
            #     string = f"Waiting for playit ping, {n}"
            #     print(string)
            #     # emit('Waiting for playit ping', {'n': f'{10-n}'}, broadcast=True)
            #     # return f"Waiting for playit ping, {10-n}"
            #     time.sleep(1)
            #     # if await applicationRunning("Playit.gg"):
            #     if await applicationRunning(playit_gg_PID, playit=True):
            #         break
            
            # if await serverOn() and await applicationRunning("Playit.gg"):
            return f"Server and playit.gg are started"
            # if await serverOn() and await applicationRunning(playit_gg_PID, playit=True):
            # else:
            #     serverStartMode = False
            #     return f"Server or playit.gg could not start, unknown cause"

        except OSError as e:
            print(OSError(f"Server error catched... Aborting!   Error was: {e}"))
            serverStartMode = False
            raise Exception(f"Server error catched... Aborting!   Error was: {e}")
            
    else:
        # return "Server is already on"
        return Home()

def updatePids():
    global serverPID, playit_gg_PID, playitCli_PID, serverProcess, playitProcess, playitCliProcess

    checkedPaths = []

    worked = False
    for knownPid in knownPidsPath.iterdir():
        pid, name, _, _, _ = Path.read_text(Path(knownPid)).split("|")
        pid = int(pid)
        if name == serverName or name == playitName or name == playitCliName:
            # mem.readMode = "normal"
            string_res, nr_res, stdIN, stdOUT, stdERR = mem.GetMemory(pid, name)
            # mem.readMode = "text"
            # string_res = mem.GetMemory(pid, name)
            if nr_res == 1:
                if name == serverName:
                    serverPID = pid
                    serverProcess = psutil.Process(pid)
                    
                elif name == playitName:
                    playit_gg_PID = pid
                    playitProcess = psutil.Process(pid)

                elif name == playitCliName:
                    playitCli_PID = pid
                    playitCliProcess = psutil.Process(pid)

                if stdIN.exists() and (stdIN != "." and stdIN != ".."):
                    checkedPaths.append(stdIN)

                if stdOUT.exists() and (stdOUT != "." and stdOUT != ".."):
                    checkedPaths.append(stdOUT)

                if stdERR.exists() and (stdERR != "." and stdERR != ".."):
                    checkedPaths.append(stdERR)

                worked = True

            if nr_res == 2 or nr_res == 4:
                if name == serverName:
                    serverProcess = None
                    
                elif name == playitName:
                    playitProcess = None

                elif name == playitCliName:
                    playitCliProcess = None

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
    if serverPID == -1 or playit_gg_PID == -1 or playitCli_PID == -1:
        if serverPID == -1:
            print(f"Checking if server is running under name: {serverName}")

        if playit_gg_PID == -1:
            print(f"Checking if playit is running under name: {playitName}")

        if playitCli_PID == -1:
            print(f"Checking if playit-cli is running under name: {playitName}")

        try:
            # p = psutil.Process(pid)

            # if serverPID == -1:
            #     if f"{p.cmdline()}".find("GT_New_Horizons_2.7.4_Server_Java_17-21") != -1:
            #         serverPID = pid
                    
            #         print(mem.Memorize(pid, serverName))

            p = findApplication("CommandLine", "GT_New_Horizons_2.7.4_Server_Java_17-21")

            if p != None:
                serverPID = p.pid
                serverProcess = psutil.Process(p.pid)
                
                print(mem.Memorize(p.pid, serverName))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            pass

        try:
            # if playit_gg_PID == -1:
            #     if f"{p.cmdline()}".find(f'$host.ui.RawUI.WindowTitle = "{playitName}"') != -1:
            #         playit_gg_PID = pid

            #         name = p.cmdline()[1].split(";")[1].replace(" $host.ui.RawUI.WindowTitle = ", "")[1:-1]
            #         print(mem.Memorize(pid, playitName))

            p = findApplication("CommandLine", f"{playitName}")

            if p != None:
                playit_gg_PID = p.pid
                playitProcess = psutil.Process(p.pid)
                
                print(mem.Memorize(p.pid, playitName))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            pass

        try:
            p = findApplication("NameUnsafe", playitCliName)

            if p != None:
                playitCli_PID = p.pid
                playitCliProcess = psutil.Process(p.pid)
                
                print(mem.Memorize(p.pid, playitCliName))    
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            pass            
                    
        if serverPID == -1:
            print(f"{serverName} could be found under name: {serverName}")

        if playit_gg_PID == -1:
            print(f"Playit could not be found under name: {playitName}")

        if playitCli_PID == -1:
            print(f"Playit could not be found under name: {playitCliName}")

@app.route('/')
def Home():
    updatePids()
    return render_template("MainPage.html")

def StartWebMonitor():
    global updateThread

    # updateThread = ControlledThread(WhileFunctionWithStop(updatePids), None, name="BackgroundUpdateThread")
    # updateThread.start()

    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    # Wait until the website is closed
    print("[internal] Waiting until website is closed")
    StartWebMonitor()

    # Stop the rest of the script
    # updateThread.stop()
    # updateThread.join(5.0) # Wait for 5 seconds in case there might be many pids to check
    print("Update thread is stopped")

    print(f"Everything has now been closed")
