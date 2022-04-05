import qi
from naoqi import ALProxy
import socket
import json
import requests
import time
import numpy as np

registration_host = "130.251.13.110"
registration_port = 9091

server_IP = "130.251.13.110"
BASE = "http://" + server_IP + ":5000/CAIR_hub"
app_name = "mainapp_multiparty"
language = "it"


class Utils(object):
    def __init__(self, logger):
        super(Utils, self).__init__()
        self.logger = logger
        self.al = ALProxy("ALAutonomousLife")
        self.memory = ALProxy("ALMemory")
        self.animated_speech = ALProxy("ALAnimatedSpeech")
        self.configuration = {"bodyLanguageMode": "contextual"}
        self.dialogue_state_file_path = "/data/home/nao/.local/share/PackageManager/apps/" + app_name + \
                                        "/dialogue_state.json"
        self.speakers_info_file_path = "/data/home/nao/.local/share/PackageManager/apps/" + app_name + \
                                       "/speakers_info.json"
        self.speakers_stats_file_path = "/data/home/nao/.local/share/PackageManager/apps/" + app_name + \
                                        "/speakers_stats.json"

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

    def compose_sentence(self, sentence_pieces):
        sentence = ""
        for elem in sentence_pieces:
            if sentence:
                sentence = sentence + " " + elem[1]
            else:
                sentence = elem[1]
        return sentence

    # This method performs a PUT request to the cloud to get the initial sentence and the dialogue state that will be used
    # for all the speakers. Then, it initializes the speakers stats and speakers info data.
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

        profile_id = "00000000-0000-0000-0000-000000000000"
        user_name = "User"
        speakers_info = {profile_id: {"name": user_name, "gender": 'nb'}}
        # Add the info of the new profile to the file where the key is the profile id and the values are the info (name)
        with open(self.speakers_info_file_path, 'w') as f:
            json.dump(speakers_info, f, ensure_ascii=False, indent=4)

        speakers_stats = {"same_interaction": [[0]],
                          "successive_interaction": [[0]],
                          "same_interaction_prob": [[0.0]],
                          "successive_interaction_prob": [[0.0]],
                          "average_topic_distance": [[0.0]],
                          "mapping_index_speaker": [profile_id],
                          "speakers_turns": [0],
                          "a_priori_prob": [0.0],
                          "speakers_moving_window": []}

        # Update the stats in the file
        with open(self.speakers_stats_file_path, 'w') as f:
            json.dump(speakers_stats, f, ensure_ascii=False, indent=4)

        self.logger("Info and statistics of the generic user have been saved in the respective files.")
        return first_dialogue_sentence, dialogue_state, speakers_info, speakers_stats

    # This method updates the info and the statistics of the users when a new user registers
    def update_speakers_statistics(self, profile_id, user_name, user_gender):
        # Load the information about the already existing users to add the new user
        with open(self.speakers_info_file_path, 'r') as info:
            speakers_info = json.load(info)
        # Load the statistics about the interactions with existing users to update them
        with open(self.speakers_stats_file_path, 'r') as stats:
            speakers_stats = json.load(stats)
        # The dimension of the square matrix will coincide with the length of the array containing the profile ids
        matrix_size = len(speakers_stats["mapping_index_speaker"])
        # For each element in the speakers_stats dictionary, add the new elements
        for elem in speakers_stats:
            if elem == "same_interaction" or elem == "successive_interaction":
                speakers_stats[elem] = np.array(speakers_stats[elem])
                speakers_stats[elem] = np.insert(speakers_stats[elem], matrix_size,
                                                 np.zeros(matrix_size, dtype=int), axis=0)
                speakers_stats[elem] = np.insert(speakers_stats[elem], matrix_size,
                                                 np.zeros(matrix_size + 1, dtype=int), axis=1)
                speakers_stats[elem] = speakers_stats[elem].tolist()
            # Add row and column to the interaction probability and average topic distance matrices
            elif elem == "same_interaction_prob" or elem == "successive_interaction_prob" or \
                    elem == "average_topic_distance":
                speakers_stats[elem] = np.array(speakers_stats[elem])
                speakers_stats[elem] = np.insert(speakers_stats[elem], matrix_size,
                                                 np.zeros(matrix_size, dtype=float), axis=0)
                speakers_stats[elem] = np.insert(speakers_stats[elem], matrix_size,
                                                 np.zeros(matrix_size + 1, dtype=float), axis=1)
                speakers_stats[elem] = speakers_stats[elem].tolist()
            # Add new profile ID to the array containing the mapping between speakers and indexes
            elif elem == "mapping_index_speaker":
                speakers_stats[elem].append(profile_id)
            # Append a new element to the list containing the number of turns of each user
            elif elem == "speakers_turns":
                speakers_stats[elem].append(0)
            # Append a new element to keep into account the a priori probability that the new user talks
            elif elem == "a_priori_prob":
                speakers_stats[elem].append(0.0)

        # Update the stats in the file
        with open(self.speakers_stats_file_path, 'w') as f:
            json.dump(speakers_stats, f, ensure_ascii=False, indent=4)

        # Add the info of the new profile to the file where the key is the profile id and the values are the info (name)
        user_gender = user_gender.lower().strip('.,?!')
        if "female" in user_gender or "femmina" in user_gender:
            user_gender = "f"
        elif "male" in user_gender or "maschio" in user_gender:
            user_gender = "m"
        else:
            user_gender = "nb"
        speakers_info[profile_id] = {"name": user_name, "gender": user_gender}
        with open(self.speakers_info_file_path, 'w') as f:
            json.dump(speakers_info, f, ensure_ascii=False, indent=4)

        return speakers_info, speakers_stats

    # This function performs the registration of a new speaker on the Microsoft APIs
    def registration_procedure(self):
        # Establish a socket connection with the registration.py script
        client_registration_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_registration_socket.connect((registration_host, registration_port))
        # ** STEP 1 ** Create a new profile ID
        self.logger("Creating new profile ID")
        client_registration_socket.send(b"new_profile_id")
        new_profile_id = client_registration_socket.recv(256).decode('utf-8')

        # ** STEP 2 ** Ask the name to the user
        if language == "it":
            to_say = "Per favore, dimmi come ti chiami."
        else:
            to_say = "Please, tell me your name."
        self.animated_speech.say(self.voice_speed + to_say, self.configuration)
        client_registration_socket.send(b"new_profile_name")
        new_profile_name = client_registration_socket.recv(256).decode('utf-8')

        # ** STEP 3 ** Ask the gender to the user
        if language == "it":
            to_say = "Per favore, dimmi quale pronome di genere vuoi che usi quando parlo con te: femminile, maschile o neutro?"
        else:
            to_say = "Please, tell me which gender pronoun should I use when I talk with you: male, female or neutral?"
        self.animated_speech.say(self.voice_speed + to_say, self.configuration)
        client_registration_socket.send(b"new_profile_gender")
        new_profile_gender = client_registration_socket.recv(256).decode('utf-8')

        # ** STEP 4 ** Ask the user to talk for 20 seconds
        if language == "it":
            to_say = "Per favore, parla per 20 secondi in modo che io possa imparare a riconoscere la tua voce."
        else:
            to_say = "Please, talk for 20 seconds so that I can learn to recognize your voice."
        self.animated_speech.say(self.voice_speed + to_say, self.configuration)
        client_registration_socket.send(b"new_profile_enrollment")
        # Wait for the completion of the enrollment
        self.logger("*** Listening ***")
        client_registration_socket.recv(256).decode('utf-8')
        if language == "it":
            to_say = "Grazie per aver completato la registrazione " + str(new_profile_name) + "! D'ora in poi riconoscero la tua voce!"
        else:
            to_say = "Thank you for registering " + str(new_profile_name) + "! From now on I will recognize your voice."
        self.animated_speech.say(self.voice_speed + to_say, self.configuration)
        # This function updates the info and the statistics of the users, adding the new profile id and the name to the
        # speakers_info and increasing the dimensions of the structures contained in the speakers_stats.
        speakers_info, speakers_stats = self.update_speakers_statistics(new_profile_id, new_profile_name, new_profile_gender)
        return speakers_info, speakers_stats
