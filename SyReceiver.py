import threading
import SyTools

class ReceiveThread(threading.Thread):
    def __init__(self):

        threading.Thread.__init__(self,name="receivethread")

    def run(self):
        if SyTools.debug_out == 1: print "rt running!"
        while True:
            if 1:
                if SyTools.debug_con == 0:
                    buf = SyTools.sock.recv(10240)
                if SyTools.debug_out == 1: print buf
                if buf[0] == 'b':
                    if buf[1] == '1':
                        SyTools.reset_controler()
                        SyTools.mouse.move(SyTools.screen_bound[0] - SyTools.margin, int(buf[2:]))
                    elif buf[1] == '2':
                        SyTools.reset_controler()
                        SyTools.mouse.move(SyTools.margin, int(buf[2:]))
                    elif buf[1] == '3':
                        SyTools.reset_controler()
                        SyTools.mouse.move(int(buf[2:]), SyTools.margin)
                    else:  # buf[1] == 4
                        SyTools.reset_controler()
                        SyTools.mouse.move(int(buf[2:]), SyTools.screen_bound[1] - SyTools.margin)
                    SyTools.reset_controler()
                if buf[:3] == "mov":
                    pos = buf[3:].split(',')
                    SyTools.pymousepos[0] += int(pos[0])
                    SyTools.pymousepos[1] += int(pos[1])
                    SyTools.mouse.move(SyTools.pymousepos[0], SyTools.pymousepos[1])
                elif buf[:3] == "clc":
                    SyTools.mouse_button(int(buf[3:]))
                elif buf[:2] == "kd":
                    SyTools.keyboard.press_key(int(buf[2:]))
                elif buf[:2] == "ku":
                    SyTools.keyboard.release_key(int(buf[2:]))
                #elif buf[:3] == "set":
                #    pos = buf[3:].split(',')
                #    mouse.move(int(pos[0]), int(pos[1]))
                # TODO: clipboard format and data
                elif buf[:3] == "clp":
                    SyTools.set_clipboard_data(buf[3:])