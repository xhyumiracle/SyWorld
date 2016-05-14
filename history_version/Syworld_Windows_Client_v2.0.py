# -*- coding=utf-8 -*-
import socket
from pymouse import PyMouse
from pykeyboard import PyKeyboard
import time
import win32clipboard as winclip
import win32con
import threading

global sock
global mouse
global mouse_pos#mouse_pos=[x,y]
global servscr,cliscr, screenboundary
global debugout, center
global sleeptime
global my_address, my_port, my_port_file, my_address_port, my_address_port_file
global dest_address, dest_port, dest_port_file, dest_address_port, dest_address_port_file
mouse = PyMouse()
key = PyKeyboard()
mouse_pos = list(mouse.position())
debugout = 1
sleeptime = 0
screenboundary=(1279,719)
center = 1

def init():
    global mouse, key, sock
    global my_address, my_port, my_port_file, my_address_port, my_address_port_file
    global dest_address, dest_port, dest_port_file, dest_address_port, dest_address_port_file
    #my_address = '192.168.137.198'
    my_address = '172.16.7.12'
    my_port = 8001
    my_port_file = 8002
    #dest_address = '192.168.137.1'
    dest_address = '172.16.6.143'
    dest_port = 8001
    dest_port_file = 8002
    my_address_port = (my_address, my_port)
    my_address_port_file = (my_address, my_port_file)
    dest_address_port = (dest_address, dest_port)
    dest_address_port_file = (dest_address, dest_port_file)


class FileTransportThreading(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, name = "ft")

    def run(self):
        print "ft runnint!"
        global my_address_port_file, dest_address_port_file
        file_sock = sockInit(my_address_port_file, dest_address_port_file)
        while True:
            print "waiting file name"
            buf = file_sock.recv(1030)
            print "file name: "+buf
            file_name = buf
            fd = None
            try:
                fd = open("c:/"+file_name, "ab")
                while True:
                    buf = file_sock.recv(10300)
                    #找一下如何不让缓冲区过满而丢包
                    fd.write(buf[1:])
                    if buf[0] == '1':  # end
                        break
            except Exception as e:
                print e
            finally:
                fd.close()

            break
        print "ft end!"


# TODO: bug:sometimes cursor will move up or down automaticly
def movMousePos(pos):#pos=[x,y]
    global mouse,mouse_pos, debugout, screenboundary, center, dest_address_port
    mouse_pos = list(mouse.position())
    mouse_pos[0] += pos[0]
    mouse_pos[1] += pos[1]
    mouse.move(mouse_pos[0],mouse_pos[1])
    if center == 1 and mouse_pos[0] <= 0:
        sock.sendto('clp'+get_clipboard_data(), dest_address_port)#from 6 to 5
        sock.sendto('b1'+str(mouse_pos[1]), dest_address_port)#from 6 to 5
        if debugout == 1: print 'b1'+str(mouse_pos[1])
        center = 0
    elif center == 1 and mouse_pos[0] >= screenboundary[0]:
        sock.sendto('clp'+get_clipboard_data(), dest_address_port)#from 6 to 5
        sock.sendto('b2'+str(mouse_pos[1]), dest_address_port)#from 4 to 5
        if debugout == 1: print 'b2'+str(mouse_pos[1])
        center = 0
    elif center == 1 and mouse_pos[1] >= screenboundary[1]:
        sock.sendto('clp'+get_clipboard_data(), dest_address_port)#from 6 to 5
        sock.sendto('b3'+str(mouse_pos[0]), dest_address_port)#from 2 to 5
        if debugout == 1: print 'b3'+str(mouse_pos[0])
        center = 0
    elif center == 1 and mouse_pos[1] <= 0:
        sock.sendto('clp'+get_clipboard_data(), dest_address_port)#from 6 to 5
        sock.sendto('b4'+str(mouse_pos[0]), dest_address_port)#from 8 to 5
        if debugout == 1: print 'b4'+str(mouse_pos[0])
        center = 0
    else: center = 1
    if debugout == 1:print "mov" + str(pos)

    if debugout == 1: print "mov" + str(pos)


def setMousePos(pos):#pos=[x,y]
    global mouse,mouse_pos
    mouse.move(pos[0],pos[1])
    mouse_pos=pos
    if debugout == 1:print "set" + str(pos)


def sockInit(address_port, destination):
    global dest_address_port
    print "sockInit "+str(address_port)
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    soc.bind(address_port)
    print "sendto"+str(destination)
    soc.sendto("hi!!", destination)
    print "sended!"
    return soc


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
    buf = sock.recv(10240)
    if buf[:3] == "mov":
        pos = buf[3:].split(',')
        pos[0]=int(pos[0])
        pos[1]=int(pos[1])
        movMousePos([pos[0], pos[1]])
    elif buf[:3] == "clc":
        mouseButton(int(buf[3:]))
    elif buf[:2] == "kd":
        key.press_key(int(buf[2:]))
    elif buf[:2] == "ku":
        key.release_key(int(buf[2:]))
    elif buf[:3] == "set":
        pos = buf[3:].split(',')
        pos[0]=int(pos[0])
        pos[1]=int(pos[1])
        setMousePos(pos)
        center = 0
    elif buf[:3] == "clp":
        set_clipboard_data(buf[3:])


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
ft = FileTransportThreading()
ft.setDaemon(True)
ft.start()
sock = sockInit(my_address_port, dest_address_port)
while 1:
    sockOperate()
sockClose()
