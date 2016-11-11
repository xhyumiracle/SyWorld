from pykeyboard import PyKeyboard
from SyConfig import debug_esc

class SyKeyboard():
    keyboard = PyKeyboard()

    def build(self, sy):
        self.sy = sy

    def on_keyboard_down(self, event):
        if self.sy.status > 0:
            self.sy.sySock.socket_send("kd", str(event.KeyID), self.sy.status)
            if debug_esc == 1 and event.KeyID == 27:
                self.sy.reset_controler(True)
            return False
        return True


    def on_keyboard_up(self, event):
        if self.sy.status > 0:
            self.sy.sySock.socket_send("ku", str(event.KeyID), self.sy.status)
            return False
        return True

