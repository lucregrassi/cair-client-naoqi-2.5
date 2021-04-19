#!/usr/bin/env python
# encoding: utf-8
import qi
import sys
from naoqi import ALProxy
import requests
import argparse
import time
import os

ip = "127.0.0.1"

sys.path.append("/data/home/nao/.local/share/PackageManager/apps/caresses/otherlibs/")

class CARESSES(object):
    def __name__(self):
        return self.__class__.__name__

    def __init__(self, app):
        app.start()
        session = app.session
        self.module_name = self.__class__.__name__
        self.isAlive = True

        self.sASR = session.service("ASR2")
        self.sMemory = session.service("ALMemory")
        self.speech_reco_event = "Audio/RecognizedWords"
        self.sLife = session.service("ALAutonomousLife")
        self.sMotion = session.service("ALMotion")
        self.animated_speech = session.service("ALAnimatedSpeech")

        self.configuration = {"bodyLanguageMode": "contextual"}
        self.fromAutonomousLifeToAwake()
        self.setAutonomousAbilities(True, True, True, True, True)

    def fromAutonomousLifeToAwake(self):
        # If enabled, disable Autonomous life
        if self.sLife.getState() in ["solitary", "interactive"]:
            self.sLife.setState("disabled")

        # If "sleeping", wake up Pepper
        if not self.sMotion.robotIsWakeUp():
            self.sMotion.wakeUp()

    def setAutonomousAbilities(self, blinking, background, awareness, listening, speaking):
        self.sLife.setAutonomousAbilityEnabled("AutonomousBlinking", blinking)
        self.sLife.setAutonomousAbilityEnabled("BackgroundMovement", background)
        self.sLife.setAutonomousAbilityEnabled("BasicAwareness", awareness)
        self.sLife.setAutonomousAbilityEnabled("ListeningMovement", listening)
        self.sLife.setAutonomousAbilityEnabled("SpeakingMovement", speaking)

    def run(self):
        # Location of the API (the server it is running on)
        azure_server = "13.95.222.73"
        cineca = "131.175.198.134"
        BASE = "http://" + cineca + ":5000/"

        client_id = -1
        if os.path.exists("credentials.txt"):
            with open("credentials.txt", 'r') as f:
                client_id = f.readline()
            self.animated_speech.say("I missed you! What would you like to talk about?", self.configuration)

        if client_id == -1:
            response = requests.put(BASE + "caresses/0/0", verify=False)
            client_id = response.json()['id']
            with open("credentials.txt", 'w') as credentials:
                credentials.write(str(client_id))
            self.animated_speech.say("Your client ID is " + str(client_id) + "Let's talk!", self.configuration)

        while self.isAlive:
            self.sASR.startReco("English", False, True)
            self.setAutonomousAbilities(True, True, True, True, True)

            start_time_silence = time.time() + 1800

            sentence = ""
            reco_speech = self.sMemory.getData(self.speech_reco_event)
            print(reco_speech)
            stop = False

            while True:
                while not reco_speech:
                    if sentence and time.time() - start_time_silence > 0.1:
                        self.sASR.stopReco()
                        self.setAutonomousAbilities(False, True, True, True, True)
                        stop = True
                        break
                    reco_speech = self.sMemory.getData(self.speech_reco_event)
                    print reco_speech
                sys.stdout.flush()
                if stop:
                    break
                if sentence == "":
                    sep = ""
                else:
                    sep = " "

                if reco_speech:
                    sentence = sentence + sep + reco_speech[0][0]
                start_time_silence = time.time()
                self.sMemory.insertData(self.speech_reco_event, [])
                reco_speech = self.sMemory.getData(self.speech_reco_event)

                if "stop talking" in sentence.lower() or "close the application" in sentence.lower():
                    self.isAlive = False
                    self.animated_speech.say("Ok, thank you for talking with me!", self.configuration)
                    exit()
                time.sleep(0.2)

            sentence = sentence.replace(" ", "_")
            print sentence
            self.sMemory.insertData(self.speech_reco_event, [])
            response = requests.get(BASE + "caresses/" + str(client_id) + "/" + sentence, verify=False)
            # print("Response time: ", response.elapsed.total_seconds())
            print response.json()['sentence']
            self.animated_speech.say(str(response.json()['sentence']), self.configuration)


def main():
    """
    Registers CARESSES as a NAOqi service.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default=ip,
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application(["CARESSES", "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) + ".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    caresses = CARESSES(app)
    caresses.run()


if __name__ == "__main__":
    main()
