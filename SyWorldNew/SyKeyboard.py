from pykeyboard import PyKeyboard
from SyConfig import debug_esc

class SyKeyboard():
    keyboard = PyKeyboard()
    key_esc = 27
    key_tab = 9
    resetHotKey = [key_esc, key_tab]
    statusHotKey = {0: 0}
    hotKeyNotPressedNum = 0
    def __init__(self):
        for k in self.resetHotKey:
            self.statusHotKey[k] = False
            self.hotKeyNotPressedNum = len(self.resetHotKey)

    def build(self, sy):
        self.sy = sy

    def sendHotKeyUp(self):
        for key_id in self.resetHotKey:
            self.sy.sySock.socket_send("ku", str(key_id), self.sy.status)

    def on_keyboard_down(self, event):
        if self.sy.status > 0:
            key_id = event.KeyID
            self.sy.sySock.socket_send("kd", str(key_id), self.sy.status)
            if (key_id in self.resetHotKey) and (not self.statusHotKey[key_id]):
                self.statusHotKey[key_id] = True
                self.hotKeyNotPressedNum -= 1
            if debug_esc == 1 and self.hotKeyNotPressedNum == 0:
                self.sendHotKeyUp()
                self.sy.reset_controler(True)
                for k in self.resetHotKey:
                    self.statusHotKey[k] = False
                    self.hotKeyNotPressedNum = len(self.resetHotKey)
            return False
            # return True
        return True


    def on_keyboard_up(self, event):
        if self.sy.status > 0:
            key_id = event.KeyID
            self.sy.sySock.socket_send("ku", str(key_id), self.sy.status)
            if (key_id in self.resetHotKey) and (self.statusHotKey[key_id]):
                self.statusHotKey[key_id] = False
                self.hotKeyNotPressedNum += 1
            return False
            # return True
        return True

