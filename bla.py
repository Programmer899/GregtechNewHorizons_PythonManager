import subprocess
import psutil

def get_process_using_port_windows(port):
    """Find which process is using a port on Windows"""
    try:
        result = subprocess.run(
            ["netstat", "-ano"], 
            capture_output=True, 
            text=True, 
            shell=True
        )
        
        for line in result.stdout.split('\n'):
            if f":{port} " in line and "LISTENING" in line:
                # Extract PID (last column)
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]

                    cmdline = ""
                    try:
                        cmdline = psutil.Process(int(pid)).cmdline()
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                        pass
                    
                    # Get process name
                    try:
                        proc_result = subprocess.run(
                            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
                            capture_output=True,
                            text=True,
                            shell=True
                        )
                        if proc_result.stdout:
                            lines = proc_result.stdout.strip().split('\n')
                            if len(lines) > 1:
                                process_name = lines[1].split(",")[0].strip('"')
                                return {"pid": pid, "process": process_name, "port": port, "cmdline": cmdline}
                    except:
                        return {"pid": pid, "process": "Unknown", "port": port, "cmdline": cmdline}
        
        return None
        
    except Exception as e:
        print(f"Error: {e}")
        return None

# Example usage
testPort = 25575
process_info = get_process_using_port_windows(testPort)
if process_info:
    print(f"Port {process_info['port']} is used by PID {process_info['pid']}: {process_info['process']}, {process_info['cmdline']}")
else:
    print(f"Port {testPort} is not in use")