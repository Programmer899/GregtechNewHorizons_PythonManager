from mcstatus import JavaServer
# from mcstatus.responses import JavaStatusResponse, QueryResponse
from mcstatus.responses import JavaStatusResponse

class ServerPingResponse():
    # def __init__(self, status: JavaStatusResponse, players: QueryResponse, latency: float = -1):
    def __init__(self, status: JavaStatusResponse, latency: float = -1):
        self.status = status
        self.latency = latency
    
    def isEmpty(self) -> bool:
        if self.latency < 0:
            return True
        return False

class ServerPing():
    def __init__(self, address: str, port: int):
        self.__address = address
        self.__port = port
        self.__server = JavaServer(self.__address, self.__port) # "localhost", 25565
    
    def Ping(self) -> ServerPingResponse|None:
        try:
            status = self.__server.status()
            # print(f"The server has {status.players.online} player(s) online and replied in {status.latency} ms")

            latency = status.latency
            # print(f"The server replied in {latency} ms")

            # query = self.__server.query(tries=10)
            # print(f"The server has the following players online: {', '.join(query.players.names)}")
        
            # return ServerPingResponse(status, query, latency)
            return ServerPingResponse(status, latency)
        except OSError as e:
            return None
