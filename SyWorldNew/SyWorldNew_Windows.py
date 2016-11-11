# -*- coding=utf-8 -*-
import win32gui
import pyHook
from SyKeyboard import SyKeyboard
from SyClipboard import SyClipboard
from SySocket import SySocket
from SyReceiver import ReceiveThread
from SyMouse import MousePosThread
from SyFileTransporter import FileTransportThread
from SyConfig import *
import sys

class SyWorld_Windows():
    status = 0
    controled = False
    controled_ip = ""
    hm = pyHook.HookManager()
    screen_bound_ui = (0, 0)
    def __init__(self):
        self.build()

    def reset_controler(self, go_center = False):
        self.status = 0
        if go_center:
            self.syMouse.mouse.move(self.screen_bound_ui[0]/2, self.screen_bound_ui[1]/2)
        self.hm.MouseMove = self.syMouse.return_true
        self.hm.MouseLeftDown = self.syMouse.on_mouse_click_status0
        self.hm.MouseLeftUp = self.syMouse.on_mouse_click_status0
        self.hm.KeyUp = self.syMouse.return_true
        self.hm.KeyDown = self.syMouse.return_true
        self.status = 0

        # TODO: ratio need float
        #BUG: mouse cannot return
        if debug_out == 1: print "reset_controler(!"

    def build(self):
        self.syClipboard = SyClipboard()
        self.syMouse = MousePosThread()
        self.syKeyboard = SyKeyboard()
        self.syFile = FileTransportThread()
        self.sySock = SySocket()
        self.syReceiver = ReceiveThread()

        self.syMouse.build(self, self.hm)
        self.syKeyboard.build(self)
        self.syFile.build(self)
        self.syReceiver.build(self)
        self.syClipboard.build(self)

    def run(self):
        self.syReceiver.setDaemon(False)
        self.syMouse.setDaemon(False)
        self.syFile.setDaemon(False)
        self.syFile.start()
        self.syReceiver.start()
        self.syMouse.start()
        self.hm.MouseLeftDown = self.syMouse.on_mouse_click_status0
        self.hm.MouseLeftUp = self.syMouse.on_mouse_click_status0
        self.hm.HookMouse()
        self.hm.HookKeyboard()
        self.syMouse.ready = True
        win32gui.PumpMessages()
        self.sySock.socket_close()

def Usage():
    something = "say something"
    print something

def main(argv):
    try:
        # opts, args = getopt.getopt(argv[1:], 'd:', ['destination='])
        opts, args = getopt.getopt(argv[1:], 'h:', ['help'])
    except getopt.GetoptError, err:
        print err
        Usage()
        sys.exit(2)

    for o, a in opts:
        if o in ['-h', '--help']:
            Usage()

#   __main__
# if __name__ == '__main__':
#     main(sys.argv)
# else:
syWorld = SyWorld_Windows()
syWorld.run()
