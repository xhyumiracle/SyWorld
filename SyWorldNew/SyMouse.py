import threading
import time
from pymouse import PyMouse
from SyConfig import *

class MousePosThread(threading.Thread):
    mouse = PyMouse()
    ready = False
    is_mouse_left_down = False
    mouse_left_down_pos = (0, 0)
    mouse_pos_hide = (0, 0)
    pymousepos = []
    # pymousepos_old = []
    ratio_pos = (1, 1)
    def __init__(self):
        threading.Thread.__init__(self, name="mt")

    def build(self, sy, hm):
        self.sy = sy
        self.hm = hm

    def __get_max_and_hide_pos(self):
        maxpos = 1000000000
        time.sleep(0.001)
        self.hm.MouseLeftDown = self.clc_set_bound
        self.hm.MouseMove = self.return_false
        pos = self.mouse.position()
        self.mouse.click(maxpos, maxpos, 1)
        self.hm.MouseLeftDown = self.clc_set_hide_pos
        print 'before hide click test, screen bound ui', self.sy.screen_bound_ui
        self.mouse.click(self.sy.screen_bound_ui[0], self.sy.screen_bound_ui[1]/2, 1)
        self.mouse.move(pos[0], pos[1])
        self.hm.MouseMove = self.return_true
        self.hm.MouseLeftDown = self.on_mouse_click_status0

    # every status = 0 should follow something like hm.keyboard = on_return_ture
    def on_mouse_move(self, event):
        if self.sy.status > 0:
            mouse_pos = event.Position
            print 'mouse pos hide', self.mouse_pos_hide
            self.sy.sySock.socket_send("mov", str(int((mouse_pos[0] - self.mouse_pos_hide[0]) * self.ratio_pos[0])) + ',' + str(int((mouse_pos[1] - self.mouse_pos_hide[1])* self.ratio_pos[1])), self.sy.status)
            # sySock.socket_send("mov", str(mouse_pos[0] - self.mouse_pos_hide[0]) + ',' + str(mouse_pos[1] - self.mouse_pos_hide[1]))
            return False
        return True

    def on_mouse_click(self, event):
        if self.sy.status > 0:
            self.sy.sySock.socket_send("clc", str(event.Message), self.sy.status)  #leftdown:513 leftup:514 rightdown:516 rightup:517 wheel:515??
            # sySock.socket_send("clc", str(event.Message))  #leftdown:513 leftup:514 rightdown:516 rightup:517 wheel:515??
            return False
        return True

    def on_mouse_click_status0(self, event):
        if event.Message == 513:
            self.mouse_left_down_pos = self.mouse.position()
            if debug_out:
                print "click!", self.mouse_left_down_pos
            self.is_mouse_left_down = True
        if event.Message == 514:
            self.is_mouse_left_down = False
        return True

    def mouse_button(self, msg):
        if msg == 513:
            self.mouse.press(self.pymousepos[0], self.pymousepos[1],1)
        if msg == 514:
            self.mouse.release(self.pymousepos[0], self.pymousepos[1],1)
        if msg == 516:
            self.mouse.release(self.pymousepos[0], self.pymousepos[1],2)
        if msg == 517:
            self.mouse.release(self.pymousepos[0], self.pymousepos[1],2)

    def clc_set_bound(self, event):
        print 'in clc set bound:'
        test = event.Position
        print 'event position', test
        self.sy.screen_bound_ui = self.mouse.position()
        # screen_bound_hk: only used in this function
        screen_bound_hk = event.Position
        print 'screen bound hk', screen_bound_hk
        print 'screen bound ui', self.sy.screen_bound_ui
        self.ratio_pos = (float(self.sy.screen_bound_ui[0])/float(screen_bound_hk[0]), float(self.sy.screen_bound_ui[1])/float(screen_bound_hk[1]))
        print "self.sy.screen_bound_ui:"+ str(self.sy.screen_bound_ui)
        print "ratio:"+str(self.ratio_pos)
        return False

    def clc_set_hide_pos(self, event):
        self.mouse_pos_hide = event.Position
        # self.mouse_pos_hide = self.mouse.position()
        print 'mouse pos hide', self.mouse_pos_hide, self.mouse.position()
        return False

    def return_true(self, event):
        return True

    def return_false(self, event):
        return False

    def run(self):
        while not self.ready:
            pass
        self.__get_max_and_hide_pos()
        if debug_out == 1:
            print "mt running!"
        set_pos_tag = False
        setpos = ""
        while True:
            if self.sy.status == 0:
                # while needmovmouse: pass
                # mlock.wait()
                self.pymousepos = list(self.mouse.position())
                if online[1] == True and self.pymousepos[0] >= self.sy.screen_bound_ui[0]: # TODO: and self.pymousepos[0]!=mouse_pos_hide[0]
                    self.sy.status = 1
                    setpos = '2'+str(float(self.pymousepos[1])/float(self.sy.screen_bound_ui[1]))  # enter right screen
                    set_pos_tag = True
                    self.sy.controled = False
                elif online[2] == True and self.pymousepos[0] <= 0:
                    self.sy.status = 2
                    setpos = '1'+str(float(self.pymousepos[1])/float(self.sy.screen_bound_ui[1]))  # enter left screen
                    set_pos_tag = True
                    self.sy.controled = False
                elif online[3] == True and self.pymousepos[1] <= 0:
                    self.sy.status = 3
                    setpos = '4'+str(float(self.pymousepos[0])/float(self.sy.screen_bound_ui[0]))  # enter up screen
                    set_pos_tag = True
                    self.sy.controled = False
                elif online[4] == True and self.pymousepos[1] >= self.sy.screen_bound_ui[1]:
                    self.sy.status = 4
                    setpos = '3'+str(float(self.pymousepos[0])/float(self.sy.screen_bound_ui[0]))  # enter down screen
                    set_pos_tag = True
                    self.sy.controled = False
                    # mlock.done()
            elif self.sy.status > 0:
                if set_pos_tag:  # enter screen
                    # send set pos
                    self.sy.sySock.socket_send('set', setpos, self.sy.status)
                    # release mouse left if is dragging file
                    if debug_out:
                        print "is_mouse_left_down: " + str(self.is_mouse_left_down)
                    if self.is_mouse_left_down:
                        # get file path
                        self.sy.syFile.files_to_send = self.sy.syClipboard.get_files_by_clipboard()
                        if self.sy.syFile.files_to_send != None:
                            self.sy.syFile.is_files_ready = True
                        if debug_out:
                            print "file ready to send"
                    else:
                        # hide pointer
                        # don't use mouse_pos_hide, since it's used in Hook
                        self.mouse.move(self.sy.screen_bound_ui[0], self.sy.screen_bound_ui[1] / 2)
                        # Hook mouse
                        self.hm.MouseMove = self.on_mouse_move
                    self.hm.MouseAllButtons = self.on_mouse_click
                    self.hm.KeyUp = self.sy.syKeyboard.on_keyboard_up
                    self.hm.KeyDown = self.sy.syKeyboard.on_keyboard_down
                    # pyHook.HookManager.HookMouse
                    self.sy.sySock.socket_send('clp', self.sy.syClipboard.get_clipboard_data(), self.sy.status)
                    set_pos_tag = False

