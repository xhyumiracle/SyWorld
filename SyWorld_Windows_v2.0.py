# -*- coding=utf-8 -*-
import pyHook
from pymouse import PyMouse
import time,win32gui
import socket
import threading
import win32clipboard as winclip
import win32con

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
global clipboard_open
global my_address, my_port, my_port_file, dest_address, dest_port, dest_port_file, my_address_port, my_address_port_file, dest_address_port, dest_address_port_file

def init():
    global online, set_pos_tag, sleep_time, hm, mouse, status, screen_bound, margin, pymousepos, pymousepos_old, mouse_pos_hide, margin, clipboard_open, sock
    global my_address, my_port, my_port_file, dest_address, dest_port, dest_port_file, my_address_port, my_address_port_file, dest_address_port, dest_address_port_file
    #my_address = '192.168.137.1'
    #my_address = '172.16.6.143'
    my_address = '172.22.54.10'
    my_port = 8001
    my_port_file = 8002
    #dest_address = '192.168.137.198'
    #dest_address = '172.16.7.12'
    dest_address = '172.22.54.11'
    dest_port = 8001
    dest_port_file = 8002
    my_address_port = (my_address, my_port)
    my_address_port_file = (my_address, my_port_file)
    dest_address_port = (dest_address, my_port)
    dest_address_port_file = (dest_address, my_port_file)

    online = [False, True, True, False, False] # null, right left up down, [0] means nothing, start from 1,
    status = 0
    mouse = PyMouse()
    screen_bound = (1365L, 767L)
    margin = 10
    set_pos_tag = False
    sleep_time = 0
    clipboard_open = False
    hm = pyHook.HookManager()
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

        threading.Thread.__init__(self,name="receivethread")

    def run(self):
        global status, debug_out, debug_con, margin, mouse, screen_bound, sock
        if debug_out == 1: print "rt running!"
        while True:
            if status > 0:
                if debug_con == 0:
                    buf = sock.recv(1024)
                if debug_out == 1: print buf
                if buf[0] == 'b':
                    if buf[1] == '1':
                        mouse.move(screen_bound[0] - margin, int(buf[2:]))
                    elif buf[1] == '2':
                        mouse.move(margin, int(buf[2:]))
                    elif buf[1] == '3':
                        mouse.move(int(buf[2:]), margin)
                    else:  # buf[1] == 4
                        mouse.move(int(buf[2:]), screen_bound[1] - margin)
                    hm.MouseMove = return_true
                    hm.MouseAllButtons = return_true
                    hm.KeyUp = return_true
                    hm.KeyDown = return_true
                    status = 0
                elif buf[:3] == 'clp':
                    set_clipboard_data(buf[3:])


class SendThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, name="sendthread")

    def run(self):
        global status, debug_out, debug_con, margin, mouse, screen_bound, setpos, set_pos_tag, hm
        if debug_out == 1: print "st running!"
        while True:
            if status > 0:
                if set_pos_tag:  # enter screen
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
                    socket_send('clp', get_clipboard_data())
                    set_pos_tag = False


class FileTransportThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, name="filethread")

    def run(self):
        print "ft running!"
        global status, debug_out, debug_con, margin, mouse, screen_bound, setpos, set_pos_tag, hm
        global my_address_port_file, dest_address_port_file
        file_socket = socket_init(my_address_port_file)
        if debug_out == 1: print "ft running!"
        file_path = "f:/21.Wireless.exe"
        file_name = "21.Wireless.exe"
        if debug_out == 1: print "send file name to "+str(dest_address_port_file)
        file_socket.sendto(file_name, dest_address_port_file)
        if debug_out == 1: print "file name sended!"
        for chunk in read_file_by_chunk(file_path, 128):
            file_socket.sendto('0'+chunk, dest_address_port_file)
        file_socket.sendto('1', dest_address_port_file)
        file_socket.close()
        if debug_out == 1: print "ft end!"


def read_file_by_chunk(filename, chunksize = 1024):
    file_obj = None
    try:
        file_obj = open(filename,'rb')
        while True:
            chunk = file_obj.read(chunksize)
            if not chunk:
                break
            yield chunk
    except Exception as e:
        print e
    finally:
        if file_obj: file_obj.close()


#
#               TYPE    TYPE-mean       STR-mean
# MouseEnter    set     setmousepos     x,y
# MouseMove     mov     movemouseto     x,y
# MouseClick    clc     click           l/r
#
# TODO:use status to judge to which screen should we send msg
def socket_send(op, arg):
    global sleep_time, debug_out, debug_con, sock, dest_address_port
    # time.sleep(sleeptime)
    if op == "set":
        sendstr = "set" + arg
    elif op == "mov":
        sendstr = "mov" + arg
    elif op == "clc":
        sendstr = "clc" + arg
    elif op == "kd":  # keyboard down
        sendstr = "kd" + arg
    elif op == "ku":  # keyboard up
        sendstr = "ku" + arg
    elif op == "clp":  # keyboard up
        sendstr = "clp" + arg
    else:
        sendstr = arg
    if debug_out == 1:print sendstr
    if debug_con == 0:sock.sendto(sendstr, dest_address_port)


# every status = 0 should follow something like hm.keyboard = on_return_ture
def on_mouse_move(event):
    global mouse_pos_hide, status, screen_bound, dest_address_port
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
        if debug_esc == 1 and event.KeyID == 27:
            reset_controler()
        return False
    return True


def on_keyboard_up(event):
    global status
    if status > 0:
        socket_send("ku", str(event.KeyID))
        return False
    return True


def get_clipboard_data():
    global clipboard_open
    d = ""
    try:
        while clipboard_open: pass
        winclip.OpenClipboard()
        clipboard_open = True
        d = winclip.GetClipboardData(win32con.CF_TEXT)
    except Exception as e:
        print e
        d = ""
    finally:
        winclip.CloseClipboard()
        clipboard_open = False
    return d


def set_clipboard_data(data):
    global  clipboard_open
    try:
        while clipboard_open: pass
        winclip.OpenClipboard()
        clipboard_open = True
        #if winclip.IsClipboardFormatAvailable(True):
        winclip.EmptyClipboard()
        winclip.SetClipboardData(win32con.CF_TEXT, data)
    except:
        pass
    finally:
        winclip.CloseClipboard()
        clipboard_open = False


def reset_controler():
    global status, rt, recvstoptag, debug_out
    status = 0
    mouse.move(screen_bound[0]/2, screen_bound[1]/2)
    if debug_out == 1: print "reset_controler(!"
    #recvstoptag = True


def socket_init(address_port):
    global debug_out
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.bind(address_port)
    print "socket_init " + str(address_port)
    print soc.recvfrom(100)
    print "has recved"
    return soc


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
ft = FileTransportThread()
st.setDaemon(True)
rt.setDaemon(True)
mt.setDaemon(True)
ft.setDaemon(True)
st.start()
rt.start()
mt.start()
ft.start()
if debug_con == 0:
    sock = socket_init(my_address_port)
hm.HookMouse()
hm.HookKeyboard()
win32gui.PumpMessages()
socket_close()

# TODO：stage4: 文件传输的用户友好性