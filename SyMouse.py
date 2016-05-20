import threading
import SyTools

class MousePosThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self,name="mt")

    def run(self):
        if SyTools.debug_out == 1: print "mt running!"
        set_pos_tag = False
        setpos = ""
        while True:
            if SyTools.status == 0:
                SyTools.pymousepos = list(SyTools.mouse.position())
                if SyTools.online[1] == True and SyTools.pymousepos[0] >= SyTools.screen_bound[0]:
                    SyTools.status = 1
                    setpos = '2'+str(SyTools.pymousepos[1])  # enter right screen
                    set_pos_tag = True
                elif SyTools.online[2] == True and SyTools.pymousepos[0] <= 0:
                    SyTools.status = 2
                    setpos = '1'+str(pymousepos[1])  # enter left screen
                    set_pos_tag = True
                elif SyTools.online[3] == True and SyTools.pymousepos[1] <= 0:
                    SyTools.status = 3
                    setpos = '4'+str(SyTools.pymousepos[0])  # enter up screen
                    set_pos_tag = True
                elif SyTools.online[4] == True and SyTools.pymousepos[1] >= SyTools.screen_bound[1]:
                    SyTools.status = 4
                    setpos = '3'+str(SyTools.pymousepos[0])  # enter down screen
                    set_pos_tag = True
            elif SyTools.status > 0:
                if set_pos_tag:  # enter screen
                    # send set pos
                    SyTools.socket_send('set', setpos)
                    # release mouse left if is dragging file
                    print "is_mouse_left_down: " + str(SyTools.is_mouse_left_down)
                    if SyTools.is_mouse_left_down:
                        # get file path
                        files_to_send = SyTools.get_files_by_clipboard()
                        if files_to_send != None: SyTools.is_files_ready = True
                    else:
                        # hide pointer
                        SyTools.mouse.move(SyTools.screen_bound[0], SyTools.screen_bound[1] / 2)
                        # Hook mouse
                        SyTools.hm.MouseMove = SyTools.on_mouse_move
                    SyTools.hm.MouseAllButtons = SyTools.on_mouse_click
                    SyTools.hm.KeyUp = SyTools.on_keyboard_up
                    SyTools.hm.KeyDown = SyTools.on_keyboard_down
                    # pyHook.HookManager.HookMouse
                    SyTools.socket_send('clp', SyTools.get_clipboard_data())
                    set_pos_tag = False