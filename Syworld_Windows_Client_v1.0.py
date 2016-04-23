import socket
from pymouse import PyMouse
from pykeyboard import PyKeyboard
import time
import win32clipboard as winclip
import win32con


global sock
global mouse
global mouse_pos#mouse_pos=[x,y]
global servscr,cliscr, screenboundary
global debugout, center
global sleeptime
mouse = PyMouse()
key = PyKeyboard()
mouse_pos = list(mouse.position())
debugout = 0
sleeptime = 0
screenboundary=(1365,767)
center = 1

def init():
    global mouse,key

#TODO: bug:sometimes cursor will move up or down automaticly
def movMousePos(pos):#pos=[x,y]
    global mouse,mouse_pos, debugout, screenboundary, center
    mouse_pos = list(mouse.position())
    mouse_pos[0] += pos[0]
    mouse_pos[1] += pos[1]
    mouse.move(mouse_pos[0],mouse_pos[1])
    if center == 1 and mouse_pos[0] <= 0:
        sock.send('clp#'+get_clipboard_data()+'|')#from 6 to 5
        sock.send('b#1#'+str(mouse_pos[1])+'|')#from 6 to 5
        if debugout == 1: print 'b#1#'+str(mouse_pos[1])
        center = 0
    elif center == 1 and mouse_pos[0] >= screenboundary[0]:
        sock.send('clp#'+get_clipboard_data()+'|')#from 6 to 5
        sock.send('b#2#'+str(mouse_pos[1])+'|')#from 4 to 5
        if debugout == 1: print 'b#2#'+str(mouse_pos[1])
        center = 0
    elif center == 1 and mouse_pos[1] >= screenboundary[1]:
        sock.send('clp#'+get_clipboard_data()+'|')#from 6 to 5
        sock.send('b#3#'+str(mouse_pos[0])+'|')#from 2 to 5
        if debugout == 1: print 'b#3#'+str(mouse_pos[0])
        center = 0
    elif center == 1 and mouse_pos[1] <= 0:
        sock.send('clp#'+get_clipboard_data()+'|')#from 6 to 5
        sock.send('b#4#'+str(mouse_pos[0])+'|')#from 8 to 5
        if debugout == 1: print 'b#4#'+str(mouse_pos[0])
        center = 0
    else: center = 1
    if debugout == 1:print "mov" + str(pos)

    if debugout == 1: print "mov" + str(pos)


def setMousePos(pos):#pos=[x,y]
    global mouse,mouse_pos
    mouse.move(pos[0],pos[1])
    mouse_pos=pos
    if debugout == 1:print "set" + str(pos)


def sockInit(addr, port):
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((addr, port))
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
            center = 0
        elif b[0] == "clp":
            set_clipboard_data(b[1])

def get_clipboard_data():
    winclip.OpenClipboard()
    if winclip.IsClipboardFormatAvailable(True):
        d = winclip.GetClipboardData(win32con.CF_TEXT)
    else:
        d = ""
    winclip.CloseClipboard()
    return d


def set_clipboard_data(data):
    winclip.OpenClipboard()
    if winclip.IsClipboardFormatAvailable(True):
        winclip.EmptyClipboard()
    winclip.SetClipboardData(win32con.CF_TEXT, data)
    winclip.CloseClipboard()

def sockClose():
    global sock
    sock.close()


#__main__
init()
sockInit('192.168.137.1', 8001)
while 1:
    sockOperate()
sockClose()