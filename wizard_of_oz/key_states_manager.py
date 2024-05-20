from pynput.keyboard import Listener, Controller


class KeyStatesManager:
    def __init__(self, state):
        self.keyboard = Controller()
        self.state = state

    def on_press(self, key):
        # Get the char attribute of the key. Default to the key itself for 
        # special (non-alphanumerical) keys like alt or ctrl (e.g. "Key.alt_r").
        key_name = getattr(key, "char", key)
        key_str = str(key_name)
        if key_str in self.state.key_states:
            self.state.set_key_state(key_str, True)

    def on_release(self, key):
        # Get the char attribute of the key. Default to the key itself for 
        # special (non-alphanumerical) keys like alt or ctrl (e.g. "Key.alt_r").
        key_name = getattr(key, "char", key)
        key_str = str(key_name)  
        if key_str in self.state.key_states:
            self.state.set_key_state(key_str, False)

    def start(self):
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
