# -*- coding=utf-8 -*-
import win32gui
import SyTools
import SyMouse
import SyFileTransporter
import SyReceiver

#   __main__
SyTools.debug_con = 0
SyTools.debug_esc = 1
SyTools.debug_out = 1
SyTools.init()
SyTools.sock
rt = SyReceiver.ReceiveThread()
mt = SyMouse.MousePosThread()
ft = SyFileTransporter.FileTransportThread()
rt.setDaemon(True)
mt.setDaemon(True)
ft.setDaemon(True)
# ft should start before main thread's socket_init, or file port will be blocked by main port's recv()
ft.start()
if SyTools.debug_con == 0:
    sock = SyTools.socket_init(SyTools.my_address_port)
# other threads especially st & rt should start after main's socket_init for they use the global var 'sock'
rt.start()
mt.start()
SyTools.hm.MouseAllButtons = SyTools.on_mouse_click_status0
#hm.KeyUp = keytest
SyTools.hm.HookMouse()
SyTools.hm.HookKeyboard()
win32gui.PumpMessages()
SyTools.socket_close()