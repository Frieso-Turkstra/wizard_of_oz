import threading
import datetime
import pandas as pd


class SharedStateManager:
    def __init__(self):
        # threading.Lock() provides a thread-safe way of setting/getting data.
        self.lock = threading.Lock()
        self.keys = ["Key.left", "Key.right", "Key.up", "Key.down", "Key.ctrl_l", "Key.ctrl_r", "Key.alt_l", "Key.alt_r"]
        self.key_states = {key: False for key in self.keys}
        self.wizard_speech = ""
        self.location = ""
        self.listening = False
        self.thinking = False
        self.volume = -1
        self.scenario = 1

    def log(self, action, value):
        # Timestamp and log every action of the wizard.
        timestamp = datetime.datetime.now().time()
        log = {"timestamp": [timestamp], "action": [action], "value": [value]}
        pd.DataFrame(log).to_csv("logs.csv", mode="a", header=False, index=False)
    
    def set_wizard_speech(self, message):
        with self.lock:
            self.wizard_speech = message
            self.log("wizard", message)
    
    def get_wizard_speech(self):
        with self.lock:
            value = self.wizard_speech
            self.wizard_speech = "" # reset after reading
            return value
    
    def set_location(self, location):
        with self.lock:
            self.location = location
            self.log("location", location)
    
    def get_location(self):
        with self.lock:
            value = self.location
            self.location = "" # reset after reading
            return value
    
    def toggle_listening(self):
        with self.lock:
            self.listening = not self.listening
            self.log("listening", self.listening)

    def get_listening(self):
        with self.lock:
            return self.listening

    def toggle_thinking(self):
        with self.lock:
            self.thinking = not self.thinking
            self.log("thinking", self.thinking)
        
    def get_thinking(self):
        with self.lock:
            return self.thinking
        
    def set_volume(self, volume):
        with self.lock:
            self.volume = volume
            self.log("volume", volume)
    
    def get_volume(self):
        with self.lock:
            value = self.volume
            self.volume = -1 # reset after reading
            return value
        
    def set_key_state(self, key, value):
        with self.lock:
            self.key_states[key] = value
            self.log("keys", self.key_states)

    def get_key_states(self):
        with self.lock:
            return self.key_states
        
    def set_scenario(self, scenario):
        with self.lock:
            self.scenario = scenario
            self.log("scenario", scenario)
