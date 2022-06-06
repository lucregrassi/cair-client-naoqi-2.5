import qi
import requests
import json
from naoqi import ALProxy

server_IP = "131.175.205.146"
BASE = "http://" + server_IP + ":5000/CAIR_hub"
app_name = "mainapp_single"
language = "it"

class Utils(object):
    def __init__(self, logger):
        super(Utils, self).__init__()
        self.logger = logger
        self.al = ALProxy("ALAutonomousLife")
        self.ba = ALProxy("ALBasicAwareness")
        self.dialogue_state_file_path = "/data/home/nao/.local/share/PackageManager/apps/" + app_name + \
                                        "/dialogue_state.json"

    def setAwareness(self):
        self.al.setAutonomousAbilityEnabled("AutonomousBlinking", True)
        self.al.setAutonomousAbilityEnabled("BackgroundMovement", True)
        # Enabled by default when in solitary or interactive, not when disabled
        self.al.setAutonomousAbilityEnabled("BasicAwareness", True)
        self.al.setAutonomousAbilityEnabled("ListeningMovement", True)
        self.al.setAutonomousAbilityEnabled("SpeakingMovement", True)
        self.ba.setEngagementMode("Unengaged")
        self.ba.setTrackingMode("Head")
        
    # This method performs a PUT request to the cloud to get the initial sentence and the dialogue state that will be used for all the speakers.
    def acquire_initial_state(self):
        # Registration of the first "unknown" user
        # Try to contact the server
        resp = requests.put(BASE, verify=False)
        first_dialogue_sentence = resp.json()["first_sentence"]
        dialogue_state = resp.json()['dialogue_state']

        # If the server is not up, continue trying until a response is received
        if not dialogue_state:
            self.animated_speech.say(self.voice_speed + "I'm waiting for the server...", self.configuration)
            # Keep on trying to perform requests to the server until it is reachable.
            while not dialogue_state:
                resp = requests.put(BASE, verify=False)
                dialogue_state = resp.json()['dialogue_state']
                time.sleep(1)
        # Store the dialogue state in the corresponding file
        with open(self.dialogue_state_file_path, 'w') as f:
            json.dump(dialogue_state, f, ensure_ascii=False, indent=4)

        self.logger("The dialogue state for a generic user has been saved in the file.")
        return first_dialogue_sentence, dialogue_state
