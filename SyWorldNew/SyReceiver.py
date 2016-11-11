import threading
from SyConfig import *

class ReceiveThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self,name="receivethread")

    def build(self, sy):
        self.sy = sy

    def run(self):
        if debug_out == 1: print "rt running!"
        while True:
            if 1:
                buf = ''
                if debug_con == 0:
                    buf, recip = self.sy.sySock.sock.recvfrom(10240)
                if not buf:
                    continue
                if debug_out == 1:
                    print "rec" +str(buf) + " from " + str(recip)
                if buf[0] == 'b':
                    self.sy.controled = True
                    # recip = (ip, port)
                    self.sy.controled_ip = recip[0]
                    # needmovmouse = True
                    # mlock.wait()
                    # needmovmouse = False
                    if buf[1] == '1':
                        # mouse.move(screen_bound[0] - margin, int(buf[2:]))
                        self.sy.syMouse.mouse.move(self.sy.screen_bound_ui[0] - margin, int(float(buf[2:]) * self.sy.screen_bound_ui[1]))
                    elif buf[1] == '2':
                        self.sy.syMouse.mouse.move(margin, int(float(buf[2:]) * self.sy.screen_bound_ui[1]))
                    elif buf[1] == '3':
                        self.sy.syMouse.mouse.move(int(float(buf[2:]) * self.sy.screen_bound_ui[0]), margin)
                    else:  # buf[1] == 4
                        self.sy.syMouse.mouse.move(int(float(buf[2:]) * self.sy.screen_bound_ui[0]), self.sy.screen_bound_ui[1] - margin)
                    self.sy.reset_controler()
                    # mlock.done()
                if self.sy.controled and buf[:3] == "mov":
                    pos = buf[3:].split(',')
                    self.sy.syMouse.pymousepos[0] += int(pos[0])
                    self.sy.syMouse.pymousepos[1] += int(pos[1])
                    self.sy.syMouse.mouse.move(self.sy.syMouse.pymousepos[0], self.sy.syMouse.pymousepos[1])
                elif buf[:3] == "clc":
                    self.sy.syMouse.mouse_button(int(buf[3:]))
                elif buf[:2] == "kd":
                    self.sy.syKeyboard.keyboard.press_key(int(buf[2:]))
                elif buf[:2] == "ku":
                    self.sy.syKeyboard.keyboard.release_key(int(buf[2:]))
                #elif buf[:3] == "set":
                #    pos = buf[3:].split(',')
                #    mouse.move(int(pos[0]), int(pos[1]))
                # TODO: clipboard format and data
                elif buf[:3] == "clp":
                    self.sy.syClipboard.set_clipboard_data(buf[3:])

