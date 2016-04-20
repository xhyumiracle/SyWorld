import pyHook
from pymouse import PyMouse
import time,win32gui
import socket

global screenbound
global mouse_pos_old,mouse_pos# =[]
global mouse
global status
global connection,sock
global sleeptime
global debugcon,debugesc,debugout
global servscreen,cliscreen
global screenonline

def init():
    global mouse_pos_old
    global mouse,status,screenbound
    global sleeptime
    global servscreen,cliscreen,screenonline
    sleeptime = 0
    status = 0
    mouse = PyMouse()
    mouse_pos_old = list(mouse.position())
    screenbound = (1365L, 767L)

    servscreen = 5
    cliscreen = 6
    screenonline = [0,0,0,0,0,0,0,0,0]


def socketInit(addr,port):
    global connection,socket,debugout
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((addr, port))
    sock.listen(5)
    connection,address = sock.accept()
    print connection.recv(100)


#
#               TYPE    TYPE-mean       STR-mean
# MouseEnter    set     setmousepos     x,y
# MouseMove     mov     movemouseto     x,y
# MouseClick    clc     click           l/r
#
#TODO:use status to judge to which screen should we send msg
def socketSend(type, str):
    global sleeptime,debugout,debugcon
    #time.sleep(sleeptime)
    sendstr = ""
    if type == "set":
        sendstr = "set#" + str
    elif type == "mov":
        sendstr = "mov#" + str
    elif type == "clc":
        sendstr = "clc#" + str
    elif type == "kd":#keyboard down
        sendstr = "kd#" + str
    elif type == "ku":#keyboard up
        sendstr = "ku#" + str
    else:sendstr = str
    if debugout == 1:print sendstr
    if debugcon == 0:connection.send(sendstr+'|')


def socketClose():
    global connection,sock
    connection.close()
    sock.close()


def afterConnected():
    global connection,screenbound,cliscreen,screenonline
    socketSend('','id#'+str(servscreen)+'#'+str(cliscreen))
    screenonline[cliscreen] = 1
    if debugout:print screenonline[6]


def enterScreen(screenid):
    global mouse_pos,status
    if debugout: print "enterScreen!"
    status = screenid
    socketSend("set",getSetPosStr(screenid))
    hideMouseFake()
    #print "after set: "+str(mouse_pos)


def hideMouseFake():
    global screenbound,mouse_pos_old,mouse_pos,mouse
    mouse_pos[0] = screenbound[0]
    mouse_pos[1] = screenbound[1]/2
    mouse_pos_old[0] = mouse_pos[0]
    mouse_pos_old[1] = mouse_pos[1]
    if debugout == 1:print "mouse_pos_old: "+str(mouse_pos_old)
    if debugout == 1:print "mouse_pos: "+str(mouse_pos)
    mouse.move(mouse_pos[0],mouse_pos[1])


def getSetPosStr(screenid):
    s = ""
    if screenid == 6:
        s = "0," + str(mouse_pos[1])
    elif screenid == 4:
        s = str(screenbound[0]) + "," + str(mouse_pos[1])
    elif screenid == 2:
        s = str(mouse_pos[0]) + "," + str(screenbound[1])
    elif screenid == 8:
        s = str(mouse_pos[0]) + ",0"
    return s


def getDposStr():
    global mouse_pos_old,mouse_pos
    if debugout == 1:print "mouse_pos_old: "+str(mouse_pos_old)
    if debugout == 1:print "mouse_pos: "+str(mouse_pos)
    return str(mouse_pos[0]-mouse_pos_old[0]) +","+ str(mouse_pos[1]-mouse_pos_old[1])


def onMouseMoveEvent(event):
    global mouse_pos_old, mouse_pos, status, screenbound, screenonline
    mouse_pos = list(event.Position)

    if status <= 0:
        if mouse_pos[0] >= screenbound[0] and screenonline[6] == 1:
            status = -1
            if mouse_pos[0] <=screenbound[0]:
                enterScreen(6)
        elif mouse_pos[0] <= 0 and screenonline[4] == 1:
            status = -1
            if mouse_pos[0] >= 0:
                enterScreen(4)
        elif mouse_pos[1] <= 0 and screenonline[2] == 1:
            status = -1
            if mouse_pos[1] >= 0:
                enterScreen(2)
        elif mouse_pos[1] >= screenbound[1] and screenonline[8] == 1:
            status = -1
            if mouse_pos[1] <= screenbound[1]:
                enterScreen(8)
    if status > 0:
        socketSend("mov", getDposStr())
        '''
        buf = connection.recv(1024)
        if buf != "":
            buf = buf.split('#')
            if buf[0] == 'b':
                if buf[1] == '1':
                    mouse.move(screenbound[0],int(buf[2]))
                    status = 0'''
        return False
    return True


def onMouseClickEvent(event):
    global status
    if status != 0:
        socketSend("clc",str(event.Message))  #leftdown:513 leftup:514 rightdown:516 rightup:517 wheel:515??
        return False
    return True

def resetControler():
    global status
    status = 0


def onKeyboardDownEvent(event):
    global status,debugesc
    if status != 0:
        socketSend("kd",str(event.KeyID))
        if debugesc == 1 and event.KeyID == 27: resetControler()
        return False
    return True

def onKeyboardUpEvent(event):
    global status
    if status != 0:
        socketSend("ku",str(event.KeyID))
        return False
    return True


#   __main__
debugcon = 0
debugesc = 1
debugout = 0
init()
if debugcon == 0:socketInit('192.168.191.1',8001)
afterConnected()
hm = pyHook.HookManager()
hm.MouseMove = onMouseMoveEvent
hm.MouseAllButtons = onMouseClickEvent
hm.KeyDown = onKeyboardDownEvent
hm.KeyUp = onKeyboardUpEvent
hm.HookMouse()
hm.HookKeyboard()
win32gui.PumpMessages()
socketClose()