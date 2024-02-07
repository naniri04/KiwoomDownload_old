import time

start_time = any

def time_start():
    global start_time
    start_time = time.time()
    
def time_stop() -> float:
    return (time.time() - start_time)

## Usage:
# Debugging.time_start()
# print(Debugging.time_stop())