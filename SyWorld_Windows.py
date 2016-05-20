# -*- coding=utf-8 -*-
import pyHook
from pymouse import PyMouse
from pykeyboard import PyKeyboard
import time,win32gui
import socket
import threading
import win32clipboard as winclip
import win32con
import sys
import getopt
import ConfigParser

global screen_bound_ui
global mouse, keyboard
global status
global connection, sock
global sleep_time
global debug_con,debug_esc, debug_out
global online, destination_ip_port, destination_ip_port_file
global pymousepos, pymousepos_old, mouse_pos_hide, margin # pos=[]
global hm
global clipboard_open
global my_address, my_port, my_port_file, my_address_port, my_address_port_file
global dest_address, dest_port, dest_port_file, dest_address_port, dest_address_port_file
global SOCKET_SND_BUF_SIZE, SOCKET_RCV_BUF_SIZE
global mouse_left_down_pos, is_mouse_left_down
global is_files_ready, files_to_send, mlock, needmovmouse, ratio_pos
global controled, controled_ip

def init(destaddr):
    global online, sleep_time, hm, mouse, keyboard, status, clipboard_open, sock
    global screen_bound_ui
    global pymousepos, pymousepos_old, mouse_pos_hide, margin
    global my_address, my_port, my_port_file, my_address_port, my_address_port_file
    global dest_address, dest_port, dest_port_file, dest_address_port, dest_address_port_file
    global SOCKET_SND_BUF_SIZE, SOCKET_RCV_BUF_SIZE, is_mouse_left_down, is_files_ready, mlock, needmovmouse, ratio_pos, destination_ip_port
    global destination_ip_port_file
    global controled, controled_ip

    cp = ConfigParser.ConfigParser()
    cp.read('conf.conf')
    config_section = 'info'
    # not global
    destination_ip = [0,0,0,0,0]
    online = [0,0,0,0,0]
    destination_ip_port = [0,0,0,0,0]
    destination_ip_port_file = [0,0,0,0,0]
    destination_ip[1] = cp.get(config_section, 'right')
    destination_ip[2] = cp.get(config_section, 'left')
    destination_ip[3] = cp.get(config_section, 'up')
    destination_ip[4] = cp.get(config_section, 'down')
    my_port = cp.getint(config_section, 'port')
    my_port_file = cp.getint(config_section, 'file_port')
    SOCKET_SND_BUF_SIZE = cp.getint(config_section, 'SOCKET_SND_BUF_SIZE')
    SOCKET_RCV_BUF_SIZE = cp.getint(config_section, 'SOCKET_RCV_BUF_SIZE')
    margin = cp.getint(config_section, 'margin')

    dest_port = 8001
    dest_port_file = 8002
    # for speed up
    # i: should unify with status and online index, which start with 1
    for i in [1, 2, 3, 4]:
        #TODO: check if ip correct
        if destination_ip[i] != '0':
            online[i] = True
        else:
            online[i] = False
        destination_ip_port[i] = (destination_ip[i], dest_port)
        destination_ip_port_file[i] = (destination_ip[i], dest_port_file)
    print online
    my_address = '0.0.0.0'
    dest_address = destaddr
    # TODO: tell others my port number

    # online = [False, True, True, True, True] # null, right left up down, [0] means nothing, start from 1,
    status = 0
    mouse = PyMouse()
    keyboard = PyKeyboard()
    sleep_time = 0
    clipboard_open = False
    hm = pyHook.HookManager()
    screen_bound_ui = (0, 0)
    # attention: mouse_pos_hide is used in Hook
    mouse_pos_hide = (0, 0)
    pymousepos = pymousepos_old = []
    controled = False
    controled_ip = ""

    my_address_port = (my_address, my_port)
    my_address_port_file = (my_address, my_port_file)
    dest_address_port = (dest_address, my_port)
    dest_address_port_file = (dest_address, my_port_file)

    is_mouse_left_down = False
    is_files_ready = False

    ratio_pos = (1, 1)


#  used in mouse thread
# class Lock():
#     __signal = 1
#     def __init__(self, sgn=1):
#         self.__signal = sgn
#
#     def wait(self):
#         while self.__signal <= 0:
#             pass
#         self.__signal -= 1
#
#     def done(self):
#         self.__signal += 1


# done
class MousePosThread(threading.Thread):
    ready = False
    def __init__(self):
        threading.Thread.__init__(self,name="mt")

    def __get_max_and_hide_pos(self):
        global mouse
        maxpos = 1000000000
        time.sleep(0.001)
        hm.MouseLeftDown = clc_set_bound
        hm.MouseMove = return_false
        pos = mouse.position()
        mouse.click(maxpos, maxpos, 1)
        hm.MouseLeftDown = clc_set_hide_pos
        mouse.click(screen_bound_ui[0], screen_bound_ui[1]/2, 1)
        mouse.move(pos[0], pos[1])
        hm.MouseMove = return_true
        hm.MouseLeftDown = on_mouse_click_status0


    def run(self):
        global status, debug_out, debug_con, margin, mouse, screen_bound_ui, hm, pymousepos
        global files_to_send, is_mouse_left_down, mouse_left_down_pos, is_files_ready, needmovmouse
        global controled
        while not self.ready:
            pass
        self.__get_max_and_hide_pos()
        if debug_out == 1:
            print "mt running!"
        set_pos_tag = False
        setpos = ""
        while True:
            if status == 0:
                # while needmovmouse: pass
                # mlock.wait()
                pymousepos = list(mouse.position())
                if online[1] == True and pymousepos[0] >= screen_bound_ui[0]: # TODO: and pymousepos[0]!=mouse_pos_hide[0]
                    status = 1
                    setpos = '2'+str(float(pymousepos[1])/float(screen_bound_ui[1]))  # enter right screen
                    set_pos_tag = True
                    controled = False
                elif online[2] == True and pymousepos[0] <= 0:
                    status = 2
                    setpos = '1'+str(float(pymousepos[1])/float(screen_bound_ui[1]))  # enter left screen
                    set_pos_tag = True
                    controled = False
                elif online[3] == True and pymousepos[1] <= 0:
                    status = 3
                    setpos = '4'+str(float(pymousepos[0])/float(screen_bound_ui[0]))  # enter up screen
                    set_pos_tag = True
                    controled = False
                elif online[4] == True and pymousepos[1] >= screen_bound_ui[1]:
                    status = 4
                    setpos = '3'+str(float(pymousepos[0])/float(screen_bound_ui[0]))  # enter down screen
                    set_pos_tag = True
                    controled = False
                # mlock.done()
            elif status > 0:
                if set_pos_tag:  # enter screen
                    # send set pos
                    socket_send('set', setpos, status)
                    # release mouse left if is dragging file
                    if debug_out:
                        print "is_mouse_left_down: " + str(is_mouse_left_down)
                    if is_mouse_left_down:
                        # get file path
                        files_to_send = get_files_by_clipboard()
                        if files_to_send != None:
                            is_files_ready = True
                        if debug_out:
                            print "file ready to send"
                    else:
                        # hide pointer
                        # don't use mouse_pos_hide, since it's used in Hook
                        mouse.move(screen_bound_ui[0], screen_bound_ui[1] / 2)
                        # Hook mouse
                        hm.MouseMove = on_mouse_move
                    hm.MouseAllButtons = on_mouse_click
                    hm.KeyUp = on_keyboard_up
                    hm.KeyDown = on_keyboard_down
                    # pyHook.HookManager.HookMouse
                    socket_send('clp', get_clipboard_data(), status)
                    set_pos_tag = False


class ReceiveThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self,name="receivethread")

    def run(self):
        global status, debug_out, debug_con, margin, mouse, screen_bound_ui, sock, pymousepos, needmovmouse
        global controled, controled_ip
        if debug_out == 1: print "rt running!"
        while True:
            if 1:
                buf = ''
                if debug_con == 0:
                    buf, recip = sock.recvfrom(10240)
                if not buf:
                    continue
                if debug_out == 1:
                    print "rec" +str(buf) + " from " + str(recip)
                if buf[0] == 'b':
                    controled = True
                    # recip = (ip, port)
                    controled_ip = recip[0]
                    # needmovmouse = True
                    # mlock.wait()
                    # needmovmouse = False
                    if buf[1] == '1':
                        # mouse.move(screen_bound[0] - margin, int(buf[2:]))
                        mouse.move(screen_bound_ui[0] - margin, int(float(buf[2:]) * screen_bound_ui[1]))
                    elif buf[1] == '2':
                        mouse.move(margin, int(float(buf[2:]) * screen_bound_ui[1]))
                    elif buf[1] == '3':
                        mouse.move(int(float(buf[2:]) * screen_bound_ui[0]), margin)
                    else:  # buf[1] == 4
                        mouse.move(int(float(buf[2:]) * screen_bound_ui[0]), screen_bound_ui[1] - margin)
                    reset_controler()
                    # mlock.done()
                if controled and buf[:3] == "mov":
                    pos = buf[3:].split(',')
                    pymousepos[0] += int(pos[0])
                    pymousepos[1] += int(pos[1])
                    mouse.move(pymousepos[0], pymousepos[1])
                elif buf[:3] == "clc":
                    mouse_button(int(buf[3:]))
                elif buf[:2] == "kd":
                    keyboard.press_key(int(buf[2:]))
                elif buf[:2] == "ku":
                    keyboard.release_key(int(buf[2:]))
                #elif buf[:3] == "set":
                #    pos = buf[3:].split(',')
                #    mouse.move(int(pos[0]), int(pos[1]))
                # TODO: clipboard format and data
                elif buf[:3] == "clp":
                    set_clipboard_data(buf[3:])


class FileTransportThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, name="filethread")

    def run(self):
        print "ft running!"
        global status, debug_out, debug_con, margin, mouse
        global my_address_port_file, destination_ip_port_file, is_files_ready
        chunk_size = 1024
        buf = ""
        recip = ""
        file_socket = socket_init(my_address_port_file, blocking=False)
        if debug_out == 1: print "ft running!"
        while True:
            if is_files_ready:
                print "is_files_ready!"
                for file in files_to_send:
                    file_name = file.split('\\')[-1]
                    file_socket.sendto(file_name, destination_ip_port_file[status])
                    if debug_out == 1:
                        print "send file %s to " %(file_name) +str(destination_ip_port_file[status])
                    buf = ''
                    while buf != 'begin' or recip != destination_ip_port_file[status]:
                        try:
                            buf, recip = file_socket.recvfrom(1024)
                        except Exception, e:
                            pass
                    if debug_out == 1:
                        print "file name:{} sended!".format(file_name)
                    send_count = 0
                    for chunk in read_file_by_chunk(file, chunk_size):
                        file_socket.sendto('0'+chunk, destination_ip_port_file[status])
                        send_count += 1
                        print "chunk {0} sended".format(send_count)
                        time.sleep(1.0/2048)  # change the speed from 2MB/s into 1MB/s in my test env, so won't be so ka
                        if send_count == 10:
                            buf = ''
                            while buf != "continue" or recip != destination_ip_port_file[status]:
                                try:
                                    buf, recip = file_socket.recvfrom(1024)
                                except Exception, e:
                                    pass
                            send_count = 0
                    file_socket.sendto('end', destination_ip_port_file[status])
                    print "end 1 sended"
                is_files_ready = False
            else:
                # print "no file ready"
                buf = ''
                try:
                    buf, recip = file_socket.recvfrom(1024)
                except Exception, e:
                    continue
                if buf:
                    if debug_out: print "recv file: " + buf + " from " + str(recip)
                    # just in "else"
                    file_name = buf
                    file_socket.sendto('begin', recip)
                    # TODO: already have file
                    if debug_out:
                        print "going to open file"
                    file_exist = True
                    try:
                        open("c:/" + file_name)
                    except Exception, e:
                        file_exist = False
                        if debug_out:
                            print 'creating file'
                    if file_exist:
                        print 'file already exist, cancel transporting'
                        continue
                    with open("c:/" + file_name, "ab") as fd:
                        if debug_out:
                            print 'recving: ' + file_name
                        recv_count = 0
                        while True:
                            if debug_out:
                                print 'waiting for data'
                            ip = ''
                            buf = ''
                            while not buf or ip != recip:
                                try:
                                    buf, ip = file_socket.recvfrom(1030)
                                except Exception, e:
                                    # TODO: do something
                                    pass
                            if buf[:3] == 'end':
                                break
                            recv_count += 1
                            if recv_count == 10:
                                file_socket.sendto('continue', recip)
                                recv_count = 0
                            fd.write(buf[1:])
                        if debug_out:
                            print 'recv_count' + str(recv_count)
                    if debug_out:
                        print 'finish!'
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
def socket_send(op, arg, dest_id):
    global sleep_time, debug_out, debug_con, sock, destination_ip_port
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
    if debug_out == 1:print "snd" + sendstr + ' to ' + str(destination_ip_port[dest_id])
    if debug_con == 0:sock.sendto(sendstr, destination_ip_port[dest_id])


# every status = 0 should follow something like hm.keyboard = on_return_ture
def on_mouse_move(event):
    global mouse_pos_hide, status, ratio_pos
    if status > 0:
        mouse_pos = event.Position
        socket_send("mov", str(int((mouse_pos[0] - mouse_pos_hide[0]) * ratio_pos[0])) + ',' + str(int((mouse_pos[1] - mouse_pos_hide[1])* ratio_pos[1])), status)
        return False
    return True


def on_mouse_click(event):
    global status
    if status > 0:
        socket_send("clc", str(event.Message), status)  #leftdown:513 leftup:514 rightdown:516 rightup:517 wheel:515??
        return False
    return True


def on_mouse_click_status0(event):
    global mouse_left_down_pos, is_mouse_left_down
    global debug_out
    if event.Message == 513:
        if debug_out:
            print "1click!"
        mouse_left_down_pos = mouse.position()
        is_mouse_left_down = True
    if event.Message == 514:
        is_mouse_left_down = False
    return True


def on_keyboard_down(event):
    global status, debug_esc
    if status > 0:
        socket_send("kd", str(event.KeyID), status)
        if debug_esc == 1 and event.KeyID == 27:
            reset_controler(True)
        return False
    return True


def on_keyboard_up(event):
    global status
    if status > 0:
        socket_send("ku", str(event.KeyID), status)
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
    global clipboard_open, keyboard, mouse_left_down_pos, is_mouse_left_down, mouse, hm, screen_bound_ui
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
        # don't use mouse_pos_hide, since it's used in Hook
        mouse.move(screen_bound_ui[0], screen_bound_ui[1] / 2)
        # TODO: get mouse position by hook now as mouse_pos_hide
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
        mouse.move(screen_bound_ui[0]/2, screen_bound_ui[1]/2)
    hm.MouseMove = return_true
    hm.MouseLeftDown = on_mouse_click_status0
    hm.MouseLeftUp = on_mouse_click_status0
    hm.KeyUp = return_true
    hm.KeyDown = return_true
    status = 0

# TODO: ratio need float
    #BUG: mouse cannot return
    if debug_out == 1: print "reset_controler(!"


def socket_init(address_port, blocking=True):
    global debug_out
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SOCKET_SND_BUF_SIZE)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, SOCKET_RCV_BUF_SIZE)
    soc.bind(address_port)
    soc.setblocking(blocking)
    print "socket_init " + str(address_port)
    #print soc.recvfrom(100)
    return soc


def socket_close():
    global connection, sock
    connection.close()
    sock.close()


def clc_set_bound(event):
    global screen_bound_ui, ratio_pos
    screen_bound_ui = mouse.position()
    # screen_bound_hk: only used in this function
    screen_bound_hk = event.Position
    ratio_pos = (float(screen_bound_ui[0])/float(screen_bound_hk[0]), float(screen_bound_ui[1])/float(screen_bound_hk[1]))
    print "screen_bound_ui:"+ str(screen_bound_ui)
    print "ratio:"+str(ratio_pos)
    return False

def clc_set_hide_pos(event):
    global mouse_pos_hide
    mouse_pos_hide = event.Position
    return False


def return_true(event):
    return True

def return_false(event):
    return False


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
        mouse.release(pymousepos[1], pymousepos[1],2)
    if msg == 517:
        mouse.release(pymousepos[0], pymousepos[1],2)


def Usage():
    something = "say something"
    print something


def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'd:', ['destination='])
    except getopt.GetoptError, err:
        print err
        Usage()
    for o, a in opts:
        if o in ['-d', '--destination']:
            run(a)
            print a+'###'


# def run(d = '172.22.226.10'):
def run(d = '192.168.191.1'):
    global debug_out, debug_con, debug_esc, hm, sock
    debug_con = 0
    debug_esc = 1
    debug_out = 1
    init(d)
    rt = ReceiveThread()
    mt = MousePosThread()
    ft = FileTransportThread()
    rt.setDaemon(False)
    mt.setDaemon(False)
    ft.setDaemon(False)
    # ft should start before main thread's socket_init, or file port will be blocked by main port's recv()
    ft.start()
    if debug_con == 0:
        sock = socket_init(my_address_port)
    # other threads especially st & rt should start after main's socket_init for they use the global var 'sock'
    rt.start()
    mt.start()
    hm.MouseLeftDown = on_mouse_click_status0
    hm.MouseLeftUp = on_mouse_click_status0
    #hm.KeyUp = keytest
    hm.HookMouse()
    hm.HookKeyboard()
    mt.ready = True
    win32gui.PumpMessages()
    socket_close()


#   __main__
# if __name__ == '__main__':
#     main(sys.argv)
# else:
print "ha"
run()
