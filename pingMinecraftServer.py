from mcstatus import JavaServer
import time

try:
    server = JavaServer("localhost", 25565)

    if server.ping() != "Server did not respond with any information!":
        status = server.status()
        print(f"The server has {status.players.online} player(s) online and replied in {status.latency} ms")

        latency = status.latency
        print(f"The server replied in {latency} ms")

        query = server.query(tries=100)
        print(f"The server has the following players online: {', '.join(query.players.names)}")
except OSError as e:
    print(e)
    pass