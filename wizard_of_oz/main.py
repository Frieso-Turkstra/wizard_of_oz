from flask import Flask, jsonify
import threading
import logging

from wizard_control_panel import WizardControlPanel
from shared_state_manager import SharedStateManager
from key_states_manager import KeyStatesManager


# Suppress info-level logs so the terminal is not flooded with GET-requests.
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.WARNING)

# Start a Flask application.
app = Flask(__name__)

# Provide a thread-safe way for the GUI, keyboard listener and server
# to set and/or read the same data.
shared_state = SharedStateManager()

# This function is continuously polled by the robot.
@app.route("/get-current-state", methods=["GET"])
def get_state():
    return jsonify({
        "location": shared_state.get_location(),
        "wizard_speech": shared_state.get_wizard_speech(),
        "listening": shared_state.get_listening(),
        "thinking": shared_state.get_thinking(),
        "volume": shared_state.get_volume(),
        "keys": shared_state.get_key_states(),
    })

def start_server():
    # The reloader cannot be used in a threaded application.
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

def start_keyboard():
    KeyStatesManager(shared_state).start()

if __name__ == "__main__":
    # Run the server and keyboard listener in separate threads so they cannot
    # block the GUI on the main thread nor each other. Setting daemon to true,
    # ensures the threads are closed at the same time as the main thread.
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=start_keyboard, daemon=True).start()
    WizardControlPanel(shared_state).start()
