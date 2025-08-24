import requests

try:
    response = requests.post('http://dietpi.lindgrens.lan:8080/hello', "computerOff")
    print(response.content)
    # requests.post('http://dietpi.lindgrens.lan:8080/hello', "computerOff")
except OSError as e:
    # print(e)
    pass



import psutil

def check_port(port):
    """Check if a port is in use and return process information"""
    # for conn in psutil.net_connections(kind="inet"):
    #     # print(f"Addr: {conn.laddr}")

    #     laddr = getattr(conn, "laddr", None)
    #     if laddr:
    #         print(laddr)

    #         ip, port = laddr[0], laddr[1]
        
    #         print(ip)
    #         print(port)
    #         break

    #     if conn.laddr.port == port:
    #         try:
    #             process = psutil.Process(conn.pid)
    #             return {
    #                 "port": port,
    #                 "pid": conn.pid,
    #                 "process_name": process.name(),
    #                 "status": conn.status,
    #                 "address": conn.laddr.ip
    #             }
    #         except (psutil.NoSuchProcess, psutil.AccessDenied):
    #             return {
    #                 "port": port,
    #                 "pid": conn.pid,
    #                 "process_name": "Unknown",
    #                 "status": conn.status,
    #                 "address": conn.laddr.ip
    #             }

    for pid in psutil.pids():
        p = psutil.Process(pid)
        for conn in p.net_connections(kind="inet"):
            if conn.laddr.port == port:
                return {
                    "port": port,
                    "pid": p.pid,
                    "process_name": p.name(),
                    "status": conn.status,
                    "address": conn.laddr.ip,
                    "cmdline": p.cmdline()
                }

    return None

# Example usage
port_info = check_port(25565)
if port_info:
    print(f"Port {port_info['port']} is used by PID {port_info['pid']} ({port_info['process_name']}, {port_info['status']}, {port_info['address']}, {port_info['cmdline']})")
    pass
else:
    print("Port 80 is not in use")
