import qi
from naoqi import ALProxy
import socket
import json
import requests
import time
import numpy as np

registration_host = "130.251.13.172"
registration_port = 9091

server_IP = "130.251.13.172"
BASE = "http://" + server_IP + ":5000/CAIR_hub"


class Utils(object):
    def __init__(self, logger):
        super(Utils, self).__init__()
        self.logger = logger
        self.al = ALProxy("ALAutonomousLife")
        self.memory = ALProxy("ALMemory")
        self.animated_speech = ALProxy("ALAnimatedSpeech")
        self.configuration = {"bodyLanguageMode": "contextual"}
        self.speakers_info_file_path = "/data/home/nao/.local/share/PackageManager/apps/mainapp_multiparty/speakers_info.json"
        self.speakers_stats_file_path = "/data/home/nao/.local/share/PackageManager/apps/mainapp_multiparty/speakers_stats.json"
        
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

    # This method performs a PUT request to the cloud to get the initial state that should be associated to the user,
    # and it adds the profile id as a field of the dialogue state
    def acquire_initial_state(self, profile_id, user_name):
        # Try to contact the server
        data = {"profile_id": profile_id}
        self.logger("Acquiring user initial state")
        resp = requests.put(BASE, data=json.dumps(data), verify=False)
        dialogue_state = resp.json()['dialogue_state']

        # If the server is not up, continue trying until a response is received
        if not dialogue_state:
            self.animated_speech.say(self.voice_speed + "I'm waiting for the server...", self.configuration)
            # Keep on trying to perform requests to the server until it is reachable.
            while not dialogue_state:
                resp = requests.put(BASE, data=json.dumps(data), verify=False)
                dialogue_state = resp.json()['dialogue_state']
                time.sleep(1)

        # If it's not the first registration of a user
        if profile_id != "00000000-0000-0000-0000-000000000000":
            # Load the information about the already existing users
            with open(self.speakers_info_file_path, 'r') as info:
                profiles_dict = json.load(info)
            # Load the statistics about the interactions with existing users
            with open(self.speakers_stats_file_path, 'r') as stats:
                speakers_stats = json.load(stats)
            # The dimension of the square matrix will coincide with the length of the array containing the profile ids
            matrix_size = len(speakers_stats["mapping_index_speaker"])
            for elem in speakers_stats:
                if elem == "same_interaction" or elem == "successive_interaction":
                    speakers_stats[elem] = np.array(speakers_stats[elem])
                    speakers_stats[elem] = np.insert(speakers_stats[elem], matrix_size,
                                                     np.zeros(matrix_size, dtype=int),
                                                     axis=0)
                    speakers_stats[elem] = np.insert(speakers_stats[elem], matrix_size,
                                                     np.zeros(matrix_size + 1, dtype=int), axis=1)
                    speakers_stats[elem] = speakers_stats[elem].tolist()
                # Add row and column to the interaction probability and average topic distance matrices
                elif elem == "same_interaction_prob" or elem == "successive_interaction_prob" or \
                        elem == "average_topic_distance":
                    speakers_stats[elem] = np.array(speakers_stats[elem])
                    speakers_stats[elem] = np.insert(speakers_stats[elem], matrix_size,
                                                     np.zeros(matrix_size, dtype=float),
                                                     axis=0)
                    speakers_stats[elem] = np.insert(speakers_stats[elem], matrix_size,
                                                     np.zeros(matrix_size + 1, dtype=float), axis=1)
                    speakers_stats[elem] = speakers_stats[elem].tolist()
                # Add new profile ID to the array containing the mapping between speakers and indexes
                elif elem == "mapping_index_speaker":
                    speakers_stats[elem].append(profile_id)
                else:
                    speakers_stats[elem].append(0.0)

        # If it's the registration of the first "unknown" user
        else:
            profiles_dict = {}
            speakers_stats = {"same_interaction": [[0]],
                              "successive_interaction": [[0]],
                              "same_interaction_prob": [[0.0]],
                              "successive_interaction_prob": [[0.0]],
                              "average_topic_distance": [[0.0]],
                              "mapping_index_speaker": [profile_id],
                              "a_priori_prob": [0.0], 
                              "speakers_moving_window": []}
                              
        self.animated_speech.say(self.voice_speed + "Updating statistics and info", self.configuration)
        # Update the stats in the file
        with open(self.speakers_stats_file_path, 'w') as stats:
            json.dump(speakers_stats, stats, ensure_ascii=False, indent=4)

        # Add the info of the new profile to the file where the key is the profile id and the values are the info
        profiles_dict[profile_id] = {"name": user_name, "dialogue_state": dialogue_state}
        with open(self.speakers_info_file_path, 'w') as info:
            json.dump(profiles_dict, info, ensure_ascii=False, indent=4)
        
        return resp.json()["reply"], profiles_dict, speakers_stats

    # The content of this function on Pepper will be managed by a specific behavior that will call Microsoft APIs
    # and write into the speakers_info.json file the new ID, name, and state of the user.
    def registration_procedure(self):
        client_registration_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_registration_socket.connect((registration_host, registration_port))
        # ** STEP 1 ** Create a new profile ID
        self.logger("Creating new profile id!")
        client_registration_socket.send(b"new_profile_id")
        new_profile_id = client_registration_socket.recv(256).decode('utf-8')

        # ** STEP 2 ** Ask the name to the user
        self.animated_speech.say(self.voice_speed + "Please, tell me your name.", self.configuration)
        client_registration_socket.send(b"new_profile_name")
        new_profile_name = client_registration_socket.recv(256).decode('utf-8')

        # ** STEP 3 ** Ask the user to talk for 20 seconds
        self.animated_speech.say(self.voice_speed + "Please, talk for twenty seconds...", self.configuration)
        client_registration_socket.send(b"new_profile_enrollment")
        # Wait for the completion of the enrollment
        self.logger("*** Listening ***")
        client_registration_socket.recv(256).decode('utf-8')

        # Perform a request to the cloud to get the initial state and save the information in the states file
        # This function also increases the dimension of the matrices adding a row and a column of zeros, and adds the
        # new profile id to the array that maps the indexes of the matrix to the profile ids of the speakers
        first_sentence, profiles_dict, speakers_stats = self.acquire_initial_state(new_profile_id, new_profile_name)
        return first_sentence, profiles_dict, speakers_stats



