from mcrcon import MCRcon

with MCRcon("127.0.0.1", "hyS4btw7", 25585) as mcr:
    resp = mcr.command('/shutdown')
    print(resp)

    mcr.disconnect()