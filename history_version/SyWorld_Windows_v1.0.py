import pyHook
from pymouse import PyMouse
import time,win32gui
import socket
import threading

global screen_bound
global mouse
global status
global connection,sock
global sleep_time
global debug_con,debug_esc, debug_out
global online
global setpos, set_pos_tag
global pymousepos, pymousepos_old, mouse_pos_hide, margin # pos=[]
global hm


def init():
    global online, set_pos_tag, sleep_time, hm, mouse, status, screen_bound, margin, pymousepos, pymousepos_old, mouse_pos_hide, margin
    online = [False, True, False, False, False] # [0] means nothing, start from 1, right left up down
    status = 0
    mouse = PyMouse()
    screen_bound = (1365L, 767L)
    margin = 10
    set_pos_tag = False
    sleep_time = 0
    hm = pyHook.HookManager()
    if debug_con == 0:
        socket_init('192.168.137.1', 8001)
    mouse_pos_hide = (screen_bound[0], screen_bound[1]/2)
    pymousepos = pymousepos_old = []


# done
class MousePosThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self,name="mt")

    def run(self):
        if debug_out == 1: print "mt running!"
        global status, pymousepos, mouse, setpos, set_pos_tag
        while True:
            if status == 0:
                pymousepos = list(mouse.position())
                if online[1] == True and pymousepos[0] >= screen_bound[0]:
                    status = 1
                    setpos = str(margin) + ',' + str(pymousepos[1])
                    set_pos_tag = True
                elif online[2] == True and pymousepos[0] <= 0:
                    status = 2
                    setpos = str(screen_bound[0] - margin) + ',' + str(pymousepos[1])
                    set_pos_tag = True
                elif online[3] == True and pymousepos[1] <= 0:
                    status = 3
                    setpos = str(pymousepos[0]) + ',' + str(screen_bound[1] - margin)
                    set_pos_tag = True
                elif online[4] == True and pymousepos[1] >= screen_bound[1]:
                    status = 4
                    setpos = str(pymousepos[0]) + ',' + str(margin)
                    set_pos_tag = True


class ReceiveThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self,name="rt")

    def run(self):
        global connection, status, debug_out, debug_con, margin, mouse, screen_bound
        if debug_out == 1: print "rt running!"
        while True:
            if status > 0:
                buf = ""
                if debug_con == 0:
                    while buf == "":
                        buf = connection.recv(1024)
                if debug_out == 1: print buf
                buf = buf.split('|')
                for i in range(buf.__len__()-1):
                    b = buf[i].split('#')
                    if b[0] == 'b':
                        if b[1] == '1':
                            mouse.move(screen_bound[0] - margin, int(b[2]))
                        elif b[1] == '2':
                            mouse.move(margin, int(b[2]))
                        elif b[1] == '3':
                            mouse.move(int(b[2]), margin)
                        else:  # b[1] == 4
                            mouse.move(int(b[2]), screen_bound[1] - margin)
                        hm.MouseMove = return_true
                        hm.MouseAllButtons = return_true
                        hm.KeyUp = return_true
                        hm.KeyDown = return_true
                        status = 0
                        break


class SendThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, name="st")

    def run(self):
        global connection, status, debug_out, debug_con, margin, mouse, screen_bound, setpos, set_pos_tag, hm
        if debug_out == 1: print "st running!"
        while True:
            if status > 0:
                if set_pos_tag:
                    # send set pos
                    socket_send('set', setpos)
                    # hide pointer
                    mouse.move(screen_bound[0], screen_bound[1] / 2)
                    # Hook mouse
                    hm.MouseMove = on_mouse_move
                    hm.MouseAllButtons = on_mouse_click
                    hm.KeyUp = on_keyboard_up
                    hm.KeyDown = on_keyboard_down
                    # pyHook.HookManager.HookMouse
                    set_pos_tag = False


#
#               TYPE    TYPE-mean       STR-mean
# MouseEnter    set     setmousepos     x,y
# MouseMove     mov     movemouseto     x,y
# MouseClick    clc     click           l/r
#
# TODO:use status to judge to which screen should we send msg
def socket_send(op, arg):
    global sleep_time, debug_out, debug_con, connection
    # time.sleep(sleeptime)
    if op == "set":
        sendstr = "set#" + arg
    elif op == "mov":
        sendstr = "mov#" + arg
    elif op == "clc":
        sendstr = "clc#" + arg
    elif op == "kd":# keyboard down
        sendstr = "kd#" + arg
    elif op == "ku":# keyboard up
        sendstr = "ku#" + arg
    else:
        sendstr = arg
    # if debug_out == 1:print sendstr
    if debug_con == 0:connection.send(sendstr + '|')


# every status = 0 should follow something like hm.keyboard = on_return_ture
def on_mouse_move(event):
    global mouse_pos_hide, status, screen_bound
    if status > 0:
        mouse_pos = list(event.Position)
        socket_send("mov", str(mouse_pos[0] - mouse_pos_hide[0]) + ',' + str(mouse_pos[1] - mouse_pos_hide[1]))
        return False
    return True


def on_mouse_click(event):
    global status
    if status > 0:
        socket_send("clc", str(event.Message))  #leftdown:513 leftup:514 rightdown:516 rightup:517 wheel:515??
        return False
    return True


def on_keyboard_down(event):
    global status, debug_esc
    if status > 0:
        socket_send("kd", str(event.KeyID))
        if debug_esc == 1 and event.KeyID == 27: resetControler()
        return False
    return True


def on_keyboard_up(event):
    global status
    if status > 0:
        socket_send("ku", str(event.KeyID))
        return False
    return True


def resetControler():
    global status, rt, recvstoptag
    status = 0
    #recvstoptag = True


def socket_init(addr, port):
    global connection, sock, debug_out
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((addr, port))
    sock.listen(5)
    connection, address = sock.accept()
    print connection.recv(100)


def socket_close():
    global connection, sock
    connection.close()
    sock.close()


def return_true(event):
    return True


#   __main__
debug_con = 0
debug_esc = 1
debug_out = 1
init()
st = SendThread()
rt = ReceiveThread()
mt = MousePosThread()
st.setDaemon(True)
rt.setDaemon(True)
mt.setDaemon(True)
st.start()
rt.start()
mt.start()
hm.HookMouse()
hm.HookKeyboard()
pyHook.HookManager.MouseAllButtons
win32gui.PumpMessages()
socket_close()

"""
def init():
    global mouse_pos_old
    global mouse,status,screenbound
    global sleeptime
    global servscreen,cliscreen,screenonline
    global recvtag, margin
    recvtag = False
    sleeptime = 0
    status = 0
    mouse = PyMouse()
    mouse_pos_old = list(mouse.position())
    screenbound = (1365L, 767L)

    servscreen = 5
    cliscreen = 6
    screenonline = [0,0,0,0,0,0,0,0,0]
    margin = 10




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
    global mouse_pos,status, rt, recvstoptag
    if debugout: print "enterScreen!"

    status = screenid
    socketSend("set",getSetPosStr(screenid))
    hideMouseFake()
    #recvstoptag = False
    #if not rt.isAlive(): rt.start()
    #print "after set: "+str(mouse_pos)


def resetControler():
    global status, rt, recvstoptag
    status = 0
    #recvstoptag = True


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
        s = str(margin) + "," + str(mouse_pos[1])
    elif screenid == 4:
        s = str(screenbound[0] - margin) + "," + str(mouse_pos[1])
    elif screenid == 2:
        s = str(mouse_pos[0]) + "," + str(screenbound[1] - margin)
    elif screenid == 8:
        s = str(mouse_pos[0]) + "," + str(margin)
    return s


def getDposStr():
    global mouse_pos_old,mouse_pos
    if debugout == 1:print "mouse_pos_old: "+str(mouse_pos_old)
    if debugout == 1:print "mouse_pos: "+str(mouse_pos)
    return str(mouse_pos[0]-mouse_pos_old[0]) +","+ str(mouse_pos[1]-mouse_pos_old[1])


def onMouseMoveEvent(event):
    global mouse_pos_old, mouse_pos, status, screenbound, screenonline
    if recvtag == True:
        if retside == 1:
            mouse.move(screenbound[0], retpos)
            resetControler()
    mouse_pos = list(event.Position)

    if status <= 0:
        if mouse_pos[0] >= screenbound[0] + margin and screenonline[6] == 1:
            status = -1
            if mouse_pos[0] <= screenbound[0]:
                enterScreen(6)
        elif mouse_pos[0] <= -margin and screenonline[4] == 1:
            status = -1
            if mouse_pos[0] >= 0:
                enterScreen(4)
        elif mouse_pos[1] <= -margin and screenonline[2] == 1:
            status = -1
            if mouse_pos[1] >= 0:
                enterScreen(2)
        elif mouse_pos[1] >= screenbound[1] + margin and screenonline[8] == 1:
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
    if status > 0:
        socketSend("clc",str(event.Message))  #leftdown:513 leftup:514 rightdown:516 rightup:517 wheel:515??
        return False
    return True


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
if debugcon == 0:socketInit('192.168.137.1',8001)
afterConnected()
hm = pyHook.HookManager()
hm.MouseMove = onMouseMoveEvent
hm.MouseAllButtons = onMouseClickEvent
hm.KeyDown = onKeyboardDownEvent
hm.KeyUp = onKeyboardUpEvent
#hm.UnhookMouse()
hm.HookMouse()
hm.HookKeyboard()
rt = ReceiveThread("server receiver")
rt.setDaemon(True)
recvstoptag = True
mt = UpdataMousePosThread("update mouse pos with pymouse")
mt.setDaemon(True)
rt.start()
mt.start()
win32gui.PumpMessages()
socketClose()
"""
