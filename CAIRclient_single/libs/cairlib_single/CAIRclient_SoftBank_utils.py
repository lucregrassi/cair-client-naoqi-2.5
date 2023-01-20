#!usr/bin/python -tt
# -*- coding: utf-8 -*-
import qi
from naoqi import ALProxy
import requests
import json
import time
import socket


class Utils(object):
    def __init__(self, logger, app_name, language, server_ip, port):
        super(Utils, self).__init__()
        self.logger = logger
        self.language = language
        self.server_ip = server_ip
        self.port = port
        self.request_uri = "http://" + self.server_ip + ":" + self.port + "/CAIR_hub"
        self.al = ALProxy("ALAutonomousLife")
        self.memory = ALProxy("ALMemory")
        self.animated_speech = ALProxy("ALAnimatedSpeech")
        self.configuration = {"bodyLanguageMode": "contextual"}
        self.dialogue_state_file_path = "/data/home/nao/.local/share/PackageManager/apps/" + app_name + \
                                        "/dialogue_state.json"
        self.speakers_info_file_path = "/data/home/nao/.local/share/PackageManager/apps/" + app_name + \
                                       "/speakers_info.json"
        self.dialogue_statistics_file_path = "/data/home/nao/.local/share/PackageManager/apps/" + app_name + \
                                             "/dialogue_statistics.json"

        try:
            # self.voice_speed = "\\RSPD=100\\"
            self.voice_speed = "\\RSPD=" + str(self.memory.getData("CAIR/voice_speed")) + "\\"
        except:
            self.memory.insertData("CAIR/voice_speed", 80)
            self.voice_speed = "\\RSPD=80\\"

    def setAutonomousAbilities(self, blinking, background, awareness, listening, speaking):
        self.al.setAutonomousAbilityEnabled("AutonomousBlinking", blinking)
        self.al.setAutonomousAbilityEnabled("BackgroundMovement", background)
        self.al.setAutonomousAbilityEnabled("BasicAwareness", awareness)
        self.al.setAutonomousAbilityEnabled("ListeningMovement", listening)
        self.al.setAutonomousAbilityEnabled("SpeakingMovement", speaking)
        
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
        resp = requests.get(self.request_uri, verify=False)
        first_dialogue_sentence = resp.json()["first_sentence"]
        dialogue_state = resp.json()['dialogue_state']

        # If the server is not up, continue trying until a response is received
        if not dialogue_state:
            if self.language == "it":
                to_say = "Sto cercando di connettermi al server"
            else:
                to_say = "I'm waiting for the server..."
            self.animated_speech.say(self.voice_speed + to_say, self.configuration)
            # Keep on trying to perform requests to the server until it is reachable.
            while not dialogue_state:
                resp = requests.get(self.request_uri, verify=False)
                dialogue_state = resp.json()['dialogue_state']
                time.sleep(1)
        # Store the dialogue state in the corresponding file
        with open(self.dialogue_state_file_path, 'w') as f:
            json.dump(dialogue_state, f, ensure_ascii=False, indent=4)

        self.logger("The dialogue state for a generic user has been saved in the file.")
        return first_dialogue_sentence
