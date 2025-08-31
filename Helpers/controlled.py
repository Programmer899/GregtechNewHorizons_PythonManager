import threading, uuid
from functools import wraps

# def stop_if(condition, *, message=None):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             if condition():
#                 if message:
#                     print(message)
#                 return  # Skip the function
#             return func(*args, **kwargs)
#         return wrapper
#     return decorator

class WhileFunctionWithStop:
    def __init__(self, func):
        wraps(func)(self)
        self._func = func
        self.stop_event = threading.Event()
        self.name = f"FunctionWithStop_{uuid.uuid4()}"

    def stop(self):
        self.stop_event.set()

    def stopped(self):
        return self.stop_event.is_set()

    def __call__(self, *args, **kwargs):
        hasNotBeenRunning = True
        while True:
            # Check stop condition before executing
            if self.stopped():
                print(f"{self.name} was stopped before execution.")
                break

            hasNotBeenRunning = False
                
            return self._func(self.stop_event, *args, **kwargs)
        
        if hasNotBeenRunning:
            return False
        return True

class ControlledThread(threading.Thread):
    def __init__(self, target_func: WhileFunctionWithStop, funcArgs: list|None, name: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self.target = target_func
        self.funcArgs = funcArgs

        if name == "":
            self.name = f"ControlledThread_{uuid.uuid4()}"
        else:
            self.name = name

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        try:
            self.target.stop_event = self._stop_event

            if self.funcArgs != None:
                self.target(arg for arg in self.funcArgs)
            else:
                self.target()

        except (TypeError or OSError) as e:
            print(f"[{self.name}] Could not execute: {e}")
