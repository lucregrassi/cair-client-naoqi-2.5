#!usr/bin/python -tt
# -*- coding: utf-8 -*-
import qi
from naoqi import ALProxy
import sys
import threading
import time
import re
app_name = "cairclient_single"


class ActionManager(object):
    def __init__(self, logger, client_socket):
        super(ActionManager, self).__init__()
        self.logger = logger
        self.client_socket = client_socket
        self.behavior_manager = ALProxy("ALBehaviorManager")
        self.animated_speech = ALProxy("ALAnimatedSpeech")
        self.configuration = {"bodyLanguageMode": "contextual"}
        self.memory = ALProxy("ALMemory")
        self.tablet = True
        self.language = self.memory.getData("CAIR/language")
        
        if self.language == "it":
            self.not_installed_behaviour = "Mi dispiace, l'applicazione non è installata!"
        else:
            self.not_installed_behaviour = "I'm sorry, the application is not installed!"
            
        try:
            self.tablet_service = ALProxy("ALTabletService")
        except:
            self.tablet = False
        
        try:
            self.voice_speed = "\\RSPD=85\\"
            self.memory.insertData("CAIR/voice_speed", 85)
            # self.voice_speed = "\\RSPD=" + str(self.memory.getData("CAIR/voice_speed")) + "\\"
        except:
            self.memory.insertData("CAIR/voice_speed", 100)
            self.voice_speed = "\\RSPD=100\\"

    # This thread function allows the robot to talk while it is performing the action for the corresponding greeting
    def greeting_thread(self, greeting):
        self.logger(greeting)
        if greeting == 1:
            time.sleep(2.5)
            self.tts.say("Hello")
        elif greeting == 2:
            time.sleep(3)
            self.tts.say("Namastay")
        elif greeting == 3:
            time.sleep(3)
            self.tts.say("Konnichiwa")
        self.tts.setLanguage("English")

    def acquire_microphone_input(self):
        self.logger("** Listening **")
        # Tell the audio recorder that the client is ready to listen
        # Send the sentence type so that it knows that it doesn't have to wait for a passphrase
        sentence_type = "q"
        self.client_socket.send(sentence_type.encode("utf-8"))
        sentence = self.client_socket.recv(1024).decode('utf-8')

        if sentence == "":
            if self.language == "it":
                to_say = "Mi dispiace, c'è stato qualche problema con la connessione al microfono esterno."
            else:
                to_say = "I'm sorry, something went wrong with the connection to the external microphone."
            self.animated_speech.say(self.voice_speed + to_say, self.configuration)
        else:
            sentence = str(sentence)
            sentence = sentence.replace("?", "")
            sentence = sentence.replace(",", "")
            sentence = sentence.replace(".", "")
        self.logger("Microphone function:" + sentence)
        return sentence
            
    def perform_action(self, item):
        action = re.findall("action=(\w+)", item)[0]
        self.logger(action)
        if action == "volume":
            if self.behavior_manager.isBehaviorInstalled("utility/volume"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                level = re.findall("level=(\w+)", item)[0]
                self.logger(level)
                self.memory.insertData("CAIR/volume_level", level)
                self.behavior_manager.runBehavior("utility/volume")
                while self.behavior_manager.isBehaviorRunning("utility/volume"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "voicespeed":
            if self.behavior_manager.isBehaviorInstalled("utility/voice_speed"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                level = re.findall("level=(\w+)", item)[0]
                self.logger(level)
                self.memory.insertData("CAIR/voice_speed_level", level)
                self.behavior_manager.runBehavior("utility/voice_speed")
                while self.behavior_manager.isBehaviorRunning("utility/voice_speed"):
                    time.sleep(0.1)
                self.voice_speed = "\\RSPD=" + str(self.memory.getData("CAIR/voice_speed")) + "\\"
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "hello":
            if self.behavior_manager.isBehaviorInstalled("greetings/hello"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                x = threading.Thread(target=self.greeting_thread, args=(1,))
                x.start()
                self.behavior_manager.runBehavior("greetings/hello")
                while self.behavior_manager.isBehaviorRunning("greetings/hello"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "namaste":
            if self.behavior_manager.isBehaviorInstalled("greetings/namaste"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                x = threading.Thread(target=self.greeting_thread, args=(2,))
                x.start()
                self.behavior_manager.runBehavior("greetings/namaste")
                while self.behavior_manager.isBehaviorRunning("greetings/namaste"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "konnichiwa":
            if self.behavior_manager.isBehaviorInstalled("greetings/konnichiwa"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                x = threading.Thread(target=self.greeting_thread, args=(3,))
                x.start()
                self.behavior_manager.runBehavior("greetings/konnichiwa")
                while self.behavior_manager.isBehaviorRunning("greetings/konnichiwa"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "time":
            if self.behavior_manager.isBehaviorInstalled("timetools/time"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                self.behavior_manager.runBehavior("timetools/time")
                while self.behavior_manager.isBehaviorRunning("timetools/time"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "date":
            if self.behavior_manager.isBehaviorInstalled("timetools/date"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                self.behavior_manager.runBehavior("timetools/date")
                while self.behavior_manager.isBehaviorRunning("timetools/date"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "weather":
            if self.behavior_manager.isBehaviorInstalled("weatherforecast/weather"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                city = re.findall("city=(.*)", item)[0]
                if city == "None":
                    self.animated_speech.say(self.voice_speed + "Per quale città vuoi che ti dica il meteo?", self.configuration)
                    city = self.acquire_microphone_input()
                self.logger(city)
                self.memory.insertData("CAIR/weather_city", city)
                self.behavior_manager.runBehavior("weatherforecast/weather")
                while self.behavior_manager.isBehaviorRunning("weatherforecast/weather"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "playsong":
            if self.behavior_manager.isBehaviorInstalled("musicplayer/play-song"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                title = re.findall("title=(.*)", item)[0]
                if title == "None" or "music" in title or title == "a song":
                    self.animated_speech.say(self.voice_speed + "Quale canzone vuoi ascoltare?", self.configuration)
                    title = self.acquire_microphone_input()
                    title = title.replace(" ", "_")
                self.logger("Acquired title:" + title)
                self.memory.insertData("CAIR/song_title", str(title))
                self.behavior_manager.runBehavior("musicplayer/play-song")
                while self.behavior_manager.isBehaviorRunning("musicplayer/play-song"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "playkaraoke":
            if self.behavior_manager.isBehaviorInstalled("karaokeplayer/play-karaoke"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                title = re.findall("title=(.*)", item)[0]
                if title == "None" or title == "a song":
                    self.animated_speech.say(self.voice_speed + "Di quale canzone vuoi fare il karaoke?", self.configuration)
                    title = self.acquire_microphone_input()
                self.logger(title)
                self.memory.insertData("CAIR/karaoke_title", title)
                self.behavior_manager.runBehavior("karaokeplayer/play-karaoke")
                while self.behavior_manager.isBehaviorRunning("karaokeplayer/play-karaoke"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "wikisearch":
            if self.behavior_manager.isBehaviorInstalled("wordtools/wikisearch"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                what = re.findall("what=(.*)", item)[0]
                self.logger(what)
                if what == "None":
                    self.animated_speech.say(self.voice_speed + "Cosa vuoi cercare su Wikipedia?", self.configuration)
                    what = self.acquire_microphone_input()
                self.memory.insertData("CAIR/wikisearch", what)
                self.behavior_manager.runBehavior("wordtools/wikisearch")
                while self.behavior_manager.isBehaviorRunning("wordtools/wikisearch"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "translate":
            if self.behavior_manager.isBehaviorInstalled("wordtools/translator"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                what = re.findall("what=(.*)", item)[0]
                if what == "None":
                    self.animated_speech.say(self.voice_speed + "Che cosa vorresti tradurre?", self.configuration)
                    what = self.acquire_microphone_input()
                self.logger(what)
                self.memory.insertData("CAIR/translate_text", what)
                
                language = re.findall("language=(\w+)", item)[0]
                if language == "None":
                    self.animated_speech.say(self.voice_speed + "In quale lingua vuoi tradurre?", self.configuration)
                    language = self.acquire_microphone_input()
                self.logger(language)
                self.memory.insertData("CAIR/translate_lan", language)
                
                self.behavior_manager.runBehavior("wordtools/translator")
                while self.behavior_manager.isBehaviorRunning("wordtools/translator"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "dictionary":
            if self.behavior_manager.isBehaviorInstalled("wordtools/dictionary"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                what = re.findall("what=(.*)", item)[0]
                if what == "None":
                    self.animated_speech.say(self.voice_speed + "Di quale parola vuoi che io cerchi la definizione sul dizionario?", self.configuration)
                    what = self.acquire_microphone_input()
                self.logger(str(what))
                self.memory.insertData("CAIR/dictionary", what)
                self.behavior_manager.runBehavior("wordtools/dictionary")
                while self.behavior_manager.isBehaviorRunning("wordtools/dictionary"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "move":
            if self.behavior_manager.isBehaviorInstalled("movement/move"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                where = re.findall("where=(\w+)", item)[0]
                self.logger(where)
                self.memory.insertData("CAIR/move", where)
                self.behavior_manager.runBehavior("movement/move")
                while self.behavior_manager.isBehaviorRunning("movement/move"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "go":
            if self.behavior_manager.isBehaviorInstalled("movement/move"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                where = re.findall("where=(\w+)", item)[0]
                self.logger(where)
                self.memory.insertData("CAIR/go", where)
                self.behavior_manager.runBehavior("movement/go")
                while self.behavior_manager.isBehaviorRunning("movement/go"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "learnplace":
            if self.behavior_manager.isBehaviorInstalled("movement/learn_place"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                where = re.findall("where=(.*)", item)[0]
                if where == "None":
                    self.animated_speech.say(self.voice_speed + "Che posto è questo?", self.configuration)
                    where = self.acquire_microphone_input()
                self.logger(where)
                self.memory.insertData("CAIR/learn_place", where)
                self.behavior_manager.runBehavior("movement/learn_place")
                while self.behavior_manager.isBehaviorRunning("movement/learn_place"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "setposition":
            if self.behavior_manager.isBehaviorInstalled("movement/set_position"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                where = re.findall("where=(.*)", item)[0]
                if where == "None":
                    self.animated_speech.say(self.voice_speed + "Dove mi trovo?", self.configuration)
                    where = self.acquire_microphone_input()
                self.logger(where)
                self.memory.insertData("CAIR/set_position", where)
                self.behavior_manager.runBehavior("movement/set_position")
                while self.behavior_manager.isBehaviorRunning("movement/set_position"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "goto":
            if self.behavior_manager.isBehaviorInstalled("movement/go_to"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                where = re.findall("where=(.*)", item)[0]
                if where == "None":
                    self.animated_speech.say(self.voice_speed + "Dove vuoi che vada?", self.configuration)
                    where = self.acquire_microphone_input()
                self.logger(where)
                self.memory.insertData("CAIR/go_to", where)
                self.behavior_manager.runBehavior("movement/go_to")
                while self.behavior_manager.isBehaviorRunning("movement/go_to"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "rest":
            # Check if the docking station was in the map
            if self.memory.getData("CAIR/go_to_outcome"):
                if self.tablet:
                    if self.behavior_manager.isBehaviorInstalled("movement/rest"):
                        self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                      "/apps/" + app_name + "/img/PrivacyMode.png")
                        self.behavior_manager.runBehavior("movement/rest")
                        while self.behavior_manager.isBehaviorRunning("movement/rest"):
                            time.sleep(0.1)
                    else:
                        self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)
                self.memory.removeData("CAIR/go_to_outcome")

        elif action == "wakeup":
            if self.tablet:
                if self.behavior_manager.isBehaviorInstalled("movement/wakeup"):
                    # Execute this behavior only on Pepper.
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                    self.behavior_manager.runBehavior("movement/wakeup")
                    while self.behavior_manager.isBehaviorRunning("movement/wakeup"):
                        time.sleep(0.1)
                else:
                    self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "forgetmap":
            if self.behavior_manager.isBehaviorInstalled("movement/forget_map"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/cairclient/img/ExecutionMode.png")
                self.behavior_manager.runBehavior("movement/forget_map")
                while self.behavior_manager.isBehaviorRunning("movement/forget_map"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "hug":
            if self.behavior_manager.isBehaviorInstalled("affectivecommunication/hug"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                self.behavior_manager.runBehavior("affectivecommunication/hug")
                while self.behavior_manager.isBehaviorRunning("affectivecommunication/hug"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "handshake":
            if self.behavior_manager.isBehaviorInstalled("affectivecommunication/handshake"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                self.behavior_manager.runBehavior("affectivecommunication/handshake")
                while self.behavior_manager.isBehaviorRunning("affectivecommunication/handshake"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "privacy":
            if self.behavior_manager.isBehaviorInstalled("provideprivacy/privacy"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/PrivacyMode.png")
                self.behavior_manager.runBehavior("provideprivacy/privacy")
                while self.behavior_manager.isBehaviorRunning("provideprivacy/privacy"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "followme":
            if self.behavior_manager.isBehaviorInstalled("follow-me/."):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/cairclient/img/ExecutionMode.png")
                self.behavior_manager.runBehavior("follow-me/.")
                while self.behavior_manager.isBehaviorRunning("follow-me/."):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)

        elif action == "showinstructions":
            if self.behavior_manager.isBehaviorInstalled("videoinstructions/show-instructions"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                what = re.findall("what=(.*)", item)[0]
                if what == "None" or what == "":
                    self.animated_speech.say(self.voice_speed + "Per cosa vuoi che ti mostri le istruzioni?", self.configuration)
                    what = self.acquire_microphone_input()
                self.logger(what)
                self.memory.insertData("CAIR/instructions", what)
                self.behavior_manager.runBehavior("videoinstructions/show-instructions")
                while self.behavior_manager.isBehaviorRunning("videoinstructions/show-instructions"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)
                
        elif action == "showexercise":
            if self.behavior_manager.isBehaviorInstalled("videoexercises/play-exercise"):
                if self.tablet:
                    self.tablet_service.showImage("http://" + self.tablet_service.robotIp() +
                                                  "/apps/" + app_name + "/img/ExecutionMode.png")
                what = re.findall("what=(.*)", item)[0]
                if what == "None":
                    self.animated_speech.say(self.voice_speed + "Quale gruppo muscolare vuoi allenare?", self.configuration)
                    what = self.acquire_microphone_input()
                self.logger(what)
                self.memory.insertData("CAIR/exercise", what)
                self.behavior_manager.runBehavior("videoexercises/play-exercise")
                while self.behavior_manager.isBehaviorRunning("videoexercises/play-exercise"):
                    time.sleep(0.1)
            else:
                self.animated_speech.say(self.voice_speed + self.not_installed_behavior, self.configuration)
