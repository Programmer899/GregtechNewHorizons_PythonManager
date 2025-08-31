class RepeatedFunction():
    def __init__(self, func, funcArgs: list|None):
        self._func = func
        self._funcArgs = funcArgs
        self.running = False
    
    def StartWhile(self):
        self.running = True

        if self._funcArgs != None:
            while self.running:
                self._func(arg for arg in self._funcArgs)
        else:
            while self.running:
                self._func()
    
    def Stop(self):
        self.running = False