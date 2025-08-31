import psutil

def isUserLoggedIn(checkerName: str = ""):
    if checkerName == "":
        return "Please specify name to check"

    for user in psutil.users():
        if user.name == checkerName:
            return True
            
    return False