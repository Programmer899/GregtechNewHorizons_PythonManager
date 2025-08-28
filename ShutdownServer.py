from mcrcon import MCRcon
from mcstatus import JavaServer
from flask import Response
import time

async def ShutdownServer():
# def ShutdownServer():
    """Tries to send the "/shutdown" command to the server via the set address and set port"""

    resp = Response()

    try:
        with MCRcon("127.0.0.1", "hyS4btw7", 25585) as mcr:
            cmd_resp = mcr.command('/stop')
            print(cmd_resp)

            mcr.disconnect()
        
        resp.status = 200
        resp.data = "Server has been shut down"
    except ConnectionRefusedError:
        resp.status = 503
        resp.data = "Server could not be shut down"
    
    return resp

if __name__ == "__main__":
    print(ShutdownServer())

    # with MCRcon("127.0.0.1", "hyS4btw7", 25585) as mcr:
    #     while True: