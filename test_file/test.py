# -*- coding=utf-8 -*-
from pymouse import PyMouse
mouse = PyMouse()

global mouse_pos


def mouse_button(msg):
    if msg == 513:
        mouse.press(mouse_pos[0], mouse_pos[1], 1)
    if msg == 514:
        mouse.release(mouse_pos[0], mouse_pos[1], 1)
    if msg == 516:
        mouse.release(mouse_pos[0], mouse_pos[1], 2)
    if msg == 517:
        mouse.release(mouse_pos[0], mouse_pos[1], 2)


import os, win32con
from pykeyboard import PyKeyboard

def read_file(name):
    return open(name.decode('utf-8'),"rb").read()

def file_exists(name):
    return os.path.exists(name)

def is_file(name):
    return os.path.isfile(name)

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


def mouseevent(event):
    print "MessageName:",event.MessageName
    print "Message:", event.Message
    print "Time:", event.Time
    print "Window:", event.Window
    print "WindowName:", event.WindowName
    print "Position:", event.Position
    print "Wheel:", event.Wheel
    print "Injected:", event.Injected
    print"---"
    return True
import pyHook, win32gui

def mouse_move(event):
    print event.Position
    return True


hm = pyHook.HookManager()
#hm.MouseAllButtons = mouseevent
hm.MouseMove = mouse_move
hm.HookMouse()
win32gui.PumpMessages()


#print os.makedirs("f:/test")
#fb = open("f:/test/21.Wireless.exe","ab")
#for chunk in read_file_by_chunk("f:/eless.exe"):
#    print "a"
    #fb.write(chunk)
#fb.close()
'''
print file_exists("f:/Shadowsocks.exe".decode('utf-8'))
print is_file("f:/Shadowsocks.exe".decode('utf-8'))
try:
    print os.makedirs("f:/test")
except Exception as e:
    print e
fd = open("f:/test/21.Wireless.exe","wb")
fd.write(read_file("f:/21.Wireless.exe"))
'''

def get_clipboard_data():
    try:
        formatname=""
        winclip.OpenClipboard()
        #winclip.EmptyClipboard()
        #d = winclip.GetClipboardFormatName()
        a = winclip.EnumClipboardFormats()
        #b = winclip.GetClipboardData(a)
        print a
        #winclip.SetClipboardData(a, b)
        print winclip.GetClipboardData(winclip.CF_TEXT).decode('gbk')
        '''
        d = winclip.GetClipboardData(winclip.CF_HDROP)# if winclip.IsClipboardFormatAvailable(True) else "haha"
        for file in d:
            print "file : "+file
        print d'''
    except Exception as e:
        print "error:"+str(e)
    finally:
        winclip.CloseClipboard()
    #return d


def set_clipboard_data(data):
    winclip.OpenClipboard()
    winclip.EmptyClipboard()
    winclip.SetClipboardData(win32con.CF_TEXT, data)
    winclip.CloseClipboard()

def keyboard(event):
    if event.KeyID == 27:
        key = PyKeyboard()
        print "key1"
        key.press_key(162)  # ctrl
        key.press_key(67)  # c
        key.release_key(67) # c
        key.release_key(162)  # ctrl
        print "key2"
    print event.KeyID
    return True

#    print "fafa"

#get_clipboard_data()
'''
import pyHook
hm = pyHook.HookManager()
hm.KeyDown = keyboard
hm.HookKeyboard()
import win32gui
win32gui.PumpMessages()
import pymouse
pymouse.PyMouse.relea
'''
#for file in get_clipboard_data():
#    print file
import win32clipboard as winclip
def get_clipboard():
    winclip.OpenClipboard()
    for i in range(0xd0000):
        try:
            d = winclip.GetClipboardFormatName(i)
            #a = winclip.EnumClipboardFormats()
            print str(hex(i))+" : "+str(d)
        except Exception as e:
            pass
    winclip.CloseClipboard()

