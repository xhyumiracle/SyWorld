import pyHook
from pymouse import PyMouse
from pykeyboard import PyKeyboard
import time
import socket
import win32clipboard as winclip
import win32con

global screen_bound, dest_screen_bound
global mouse, keyboard
global status
global connection
global sock
global sleep_time
global debug_con,debug_esc, debug_out
global online
global pymousepos, pymousepos_old, mouse_pos_hide, margin # pos=[]
global hm
global clipboard_open
global my_address, my_port, my_port_file, my_address_port, my_address_port_file
global dest_address, dest_port, dest_port_file, dest_address_port, dest_address_port_file
global SOCKET_SND_BUF_SIZE, SOCKET_RCV_BUF_SIZE
global mouse_left_down_pos, is_mouse_left_down
global is_files_ready, files_to_send



def init():
    global online, sleep_time, hm, mouse, keyboard, status, clipboard_open, sock
    global screen_bound, dest_screen_bound
    global pymousepos, pymousepos_old, mouse_pos_hide, margin
    global my_address, my_port, my_port_file, my_address_port, my_address_port_file
    global dest_address, dest_port, dest_port_file, dest_address_port, dest_address_port_file
    global SOCKET_SND_BUF_SIZE, SOCKET_RCV_BUF_SIZE, is_mouse_left_down, is_files_ready
    #my_address = '192.168.137.1'
    my_address = '0.0.0.0'
    my_port = 8001
    my_port_file = 8002
    #dest_address = '192.168.137.198'
    #dest_address = '172.22.188.140'
    dest_address = '192.168.30.171'
    dest_port = 8001
    dest_port_file = 8002
    SOCKET_SND_BUF_SIZE = 65536
    SOCKET_RCV_BUF_SIZE = 65536

    online = [False, True, True, False, False] # null, right left up down, [0] means nothing, start from 1,
    status = 0
    mouse = PyMouse()
    keyboard = PyKeyboard()
    screen_bound = (1365L, 767L)
    dest_screen_bound = (1279L, 719L)
    margin = 10
    sleep_time = 0
    clipboard_open = False
    hm = pyHook.HookManager()
    mouse_pos_hide = (screen_bound[0], screen_bound[1]/2)
    pymousepos = pymousepos_old = []

    my_address_port = (my_address, my_port)
    my_address_port_file = (my_address, my_port_file)
    dest_address_port = (dest_address, my_port)
    dest_address_port_file = (dest_address, my_port_file)

    is_mouse_left_down = False
    is_files_ready = False



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
        sendstr = "b" + arg  # set0,123 -> b#1#123 -> b1123
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


def on_mouse_click_status0(event):
    global mouse_left_down_pos, is_mouse_left_down
    if event.Message == 513:
        print "click!"
        mouse_left_down_pos = mouse.position()
        is_mouse_left_down = True
    if event.Message == 514:
        is_mouse_left_down = False
    return True


def on_keyboard_down(event):
    global status, debug_esc
    if status > 0:
        socket_send("kd", str(event.KeyID))
        if debug_esc == 1 and event.KeyID == 27:
            reset_controler(True)
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
    except Exception as e:
        print "set_clipboard_data(): " + str(e)
    finally:
        winclip.CloseClipboard()
        clipboard_open = False


def get_files_by_clipboard():
    global clipboard_open, keyboard, mouse_left_down_pos, is_mouse_left_down, mouse, hm, screen_bound
    files = None
    try:
        while clipboard_open: pass
        winclip.OpenClipboard()
        clipboard_open = True
        bak_fmt = winclip.EnumClipboardFormats()
        bak_data = winclip.GetClipboardData(bak_fmt)
        # mimic ctrl-c
        #if winclip.EnumClipboardFormats() == 13:
        #    print "before sleep, copy data:"+winclip.GetClipboardData(winclip.CF_TEXT)+"dataend"
        #print str(mouse_left_down_pos)
        mouse.release(mouse_left_down_pos[0], mouse_left_down_pos[1], 1)
        is_mouse_left_down = False
        #print "first sleep over"
        #winclip.EmptyClipboard()
        #winclip.SetClipboardData(win32con.CF_TEXT, "setfordetectformatschangelater")

        winclip.CloseClipboard()
        clipboard_open = False

        # hide pointer
        mouse.move(screen_bound[0], screen_bound[1] / 2)
        # Hook mouse
        hm.MouseMove = on_mouse_move
        # should be with hm.KeyUp = ... logically, but put here to give user a quick feed back that entered other screen
        # while localhost can continue its clipboard operations

        # TODO: not so graceful hear (time.sleep)
        time.sleep(0.2)
        #keyboard.tap_key(40)
        keyboard.press_key(162)  # ctrl
        keyboard.press_key(67)  # c
        keyboard.release_key(67)  # c
        keyboard.release_key(162)  # ctrl
        time.sleep(0.2)
        # TODO: how to detect clipboard open ? then i can check whether the ctrl-c had been pressed successfully
        while clipboard_open: pass
        winclip.OpenClipboard()
        clipboard_open = True

        #if winclip.EnumClipboardFormats() == 13 or winclip.EnumClipboardFormats() == 1:
        #    print "copy data:"+winclip.GetClipboardData(winclip.CF_TEXT)+"dataend"
        #print hex(winclip.EnumClipboardFormats())
        files = winclip.GetClipboardData(winclip.CF_HDROP)
        winclip.SetClipboardData(bak_fmt, bak_data)
    except Exception as e:
        print e
    finally:
        winclip.CloseClipboard()
        clipboard_open = False
    return files

def reset_controler(go_center = False):
    global status, rt, recvstoptag, debug_out, hm
    status = 0
    if go_center:
        mouse.move(screen_bound[0]/2, screen_bound[1]/2)
    hm.MouseMove = return_true
    hm.MouseAllButtons = on_mouse_click_status0
    hm.KeyUp = return_true
    hm.KeyDown = return_true
    status = 0

    if debug_out == 1: print "reset_controler(!"


def socket_init(address_port):
    global debug_out
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SOCKET_SND_BUF_SIZE)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, SOCKET_RCV_BUF_SIZE)
    soc.bind(address_port)
    print "socket_init " + str(address_port)
    #print soc.recvfrom(100)
    return soc


def socket_close():
    global connection, sock
    connection.close()
    sock.close()


def return_true(event):
    return True

def keytest(event):
    print "keytest:"+str(event.KeyID)
    return True


def mouse_button(msg):
    global mouse, pymousepos
    if msg == 513:
        mouse.press(pymousepos[0], pymousepos[1],1)
    if msg == 514:
        mouse.release(pymousepos[0], pymousepos[1],1)
    if msg == 516:
        mouse.release(pymousepos[0], pymousepos[1],2)
    if msg == 517:
        mouse.release(pymousepos[0], pymousepos[1],2)
