import socket
from pymouse import PyMouse
from pykeyboard import PyKeyboard
import time

global sock
global mouse
global mouse_pos#mouse_pos=[x,y]
global servscr,cliscr
global debugout
global sleeptime
mouse = PyMouse()
key = PyKeyboard()
mouse_pos = list(mouse.position())
debugout = 1
sleeptime = 0

def init():
    global mouse,key

#TODO: bug:sometimes cursor will move up or down automaticly
def movMousePos(pos):#pos=[x,y]
    global mouse,mouse_pos, debugout
    mouse_pos = list(mouse.position())
    mouse_pos[0] += pos[0]
    mouse_pos[1] += pos[1]
    mouse.move(mouse_pos[0],mouse_pos[1])
    '''if mouse_pos[0] <= 0 and center == 1:
        sock.send('b#1#'+str(mouse_pos[1]))#from 6 to 5
        center = 0
    elif mouse_pos[0] >= screenboudary[0] and center == 1:
        sock.send('b#2#'+str(mouse_pos[1]))#from 4 to 5
        center = 0
    elif mouse_pos[1] >= screenboudary[1] and center == 1:
        sock.send('b#3#'+str(mouse_pos[0]))#from 2 to 5
        center = 0
    elif mouse_pos[1] <= 0 and center == 1:
        sock.send('b#4#'+str(mouse_pos[0]))#from 8 to 5
        center = 0
    else: center = 1
    if debugout == 1:print "mov" + str(pos)
    '''
    if debugout == 1: print "mov" + str(pos)


def setMousePos(pos):#pos=[x,y]
    global mouse,mouse_pos
    mouse.move(pos[0],pos[1])
    mouse_pos=pos
    if debugout == 1:print "set" + str(pos)



def sockInit():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('192.168.137.1',8001))
    sock.send("hi!!")


def mouseButton(msg):
    global mouse,mouse_pos
    if msg == 513:
        mouse.press(mouse_pos[0],mouse_pos[1],1)
    if msg == 514:
        mouse.release(mouse_pos[0],mouse_pos[1],1)
    if msg == 516:
        mouse.release(mouse_pos[0],mouse_pos[1],2)
    if msg == 517:
        mouse.release(mouse_pos[0],mouse_pos[1],2)


def sockOperate():
    global sock
    buf = ""
    while buf == "":
        time.sleep(sleeptime)
        buf = sock.recv(10240)
    buf = buf.split('|')
    for i in range(buf.__len__()-1):
        b = buf[i]
        b = b.split('#')
        if b[0] == "mov":
            pos = b[1].split(',')
            pos[0]=int(pos[0])
            pos[1]=int(pos[1])
            movMousePos([pos[0],pos[1]])
        elif b[0] == "clc":
            mouseButton(int(b[1]))
        elif b[0] == "kd":
            key.press_key(int(b[1]))
        elif b[0] == "ku":
            key.release_key(int(b[1]))
        elif b[0] == "set":
            pos = b[1].split(',')
            pos[0]=int(pos[0])
            pos[1]=int(pos[1])
            setMousePos(pos)
        elif b[0] == "id":
            servscr = int(b[1])
            cliscr = int(b[2])


def sockClose():
    global sock
    sock.close()


#__main__
init()
sockInit()
while 1:
    sockOperate()
sockClose()