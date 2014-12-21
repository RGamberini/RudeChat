import sys
from select import select

std_in = [sys.stdin]
c = 0
x = 0
while True:
    readable, writable, exceptional = select(std_in, std_in, std_in, 8000)
    if x > 0:
        x -= 1
    elif c % 45000 == 0:
        c = 0
        print("Still alive")
    for returned in readable:
        if returned == sys.stdin:
            line = sys.stdin.readline()
            print(line)
            x = 300
    c += 1
