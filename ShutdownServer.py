from mcrcon import MCRcon
from mcstatus import JavaServer
import time

async def ShutdownServer():
# def ShutdownServer():
    """Tries to send the "/shutdown" command to the server via the set address and set port"""
    try:
        with MCRcon("127.0.0.1", "hyS4btw7", 25585) as mcr:
            resp = mcr.command('/stop')
            print(resp)

            mcr.disconnect()
        
        return True
    except ConnectionRefusedError:
        return False

if __name__ == "__main__":
    print(ShutdownServer())

    # with MCRcon("127.0.0.1", "hyS4btw7", 25585) as mcr:
    #     while True: