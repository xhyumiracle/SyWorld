import win32clipboard as winclip
import win32con

class SyClipboard():
    clipboard_open = False
    def build(self, sy):
        self.sy = sy

    def get_clipboard_data(self):
        d = ""
        try:
            while self.clipboard_open: pass
            winclip.OpenClipboard()
            self.clipboard_open = True
            d = winclip.GetClipboardData(win32con.CF_TEXT)
        except Exception as e:
            print e
            d = ""
        finally:
            winclip.CloseClipboard()
            self.clipboard_open = False
        return d


    def set_clipboard_data(self, data):
        try:
            while self.clipboard_open: pass
            winclip.OpenClipboard()
            self.clipboard_open = True
            #if winclip.IsClipboardFormatAvailable(True):
            winclip.EmptyClipboard()
            winclip.SetClipboardData(win32con.CF_TEXT, data)
        except Exception as e:
            print "set_clipboard_data(): " + str(e)
        finally:
            winclip.CloseClipboard()
            self.clipboard_open = False

    def get_files_by_clipboard(self):
        global clipboard_open, keyboard, mouse_left_down_pos, is_mouse_left_down, mouse, hm, screen_bound_ui
        files = None
        try:
            while self.clipboard_open: pass
            winclip.OpenClipboard()
            self.clipboard_open = True
            bak_fmt = winclip.EnumClipboardFormats()
            bak_data = winclip.GetClipboardData(bak_fmt)
            # mimic ctrl-c
            #if winclip.EnumClipboardFormats() == 13:
            #    print "before sleep, copy data:"+winclip.GetClipboardData(winclip.CF_TEXT)+"dataend"
            #print str(mouse_left_down_pos)
            self.sy.syMouse.mouse.release(self.sy.syMouse.mouse_left_down_pos[0], self.sy.syMouse.mouse_left_down_pos[1], 1)
            self.sy.syMouse.is_mouse_left_down = False
            #print "first sleep over"
            #winclip.EmptyClipboard()
            #winclip.SetClipboardData(win32con.CF_TEXT, "setfordetectformatschangelater")

            winclip.CloseClipboard()
            self.clipboard_open = False

            # hide pointer
            # don't use mouse_pos_hide, since it's used in Hook
            self.sy.syMouse.mouse.move(self.sy.screen_bound_ui[0], self.sy.screen_bound_ui[1] / 2)
            # TODO: get mouse position by hook now as mouse_pos_hide
            # Hook mouse
            self.sy.hm.MouseMove = self.sy.syMouse.on_mouse_move
            # should be with hm.KeyUp = ... logically, but put here to give user a quick feed back that entered other screen
            # while localhost can continue its clipboard operations

            # TODO: not so graceful hear (time.sleep)
            time.sleep(0.2)
            #keyboard.tap_key(40)
            self.sy.syKeyboard.keyboard.press_key(162)  # ctrl
            self.sy.syKeyboard.keyboard.press_key(67)  # c
            self.sy.syKeyboard.keyboard.release_key(67)  # c
            self.sy.syKeyboard.keyboard.release_key(162)  # ctrl
            time.sleep(0.2)
            # TODO: how to detect clipboard open ? then i can check whether the ctrl-c had been pressed successfully
            while self.clipboard_open: pass
            winclip.OpenClipboard()
            self.clipboard_open = True

            #if winclip.EnumClipboardFormats() == 13 or winclip.EnumClipboardFormats() == 1:
            #    print "copy data:"+winclip.GetClipboardData(winclip.CF_TEXT)+"dataend"
            #print hex(winclip.EnumClipboardFormats())
            files = winclip.GetClipboardData(winclip.CF_HDROP)
            winclip.SetClipboardData(bak_fmt, bak_data)
        except Exception as e:
            print e
        finally:
            winclip.CloseClipboard()
            self.clipboard_open = False
        return files

