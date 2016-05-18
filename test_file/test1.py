global a, sock
global aa, aaa
a = 1

# class c:
#     def bb(self):
#         return 10
#
# def fff():
#     global a
#     a = 10
import pymouse
import pyHook
import win32gui
def mov(event):
    print str(mouse.position()) + '###' + str(event.Position)
    return True
mouse = pymouse.PyMouse()
hm = pyHook.HookManager()
hm.MouseMove = mov
hm.HookMouse()
win32gui.PumpMessages()
