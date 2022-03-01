import qi
from naoqi import ALProxy
import threading
        
class Utils(object):
    def __init__(self, logger):
        super(Utils, self).__init__()
        self.logger = logger
        self.al = ALProxy("ALAutonomousLife")
        self.behavior_manager = ALProxy("ALBehaviorManager")
        self.tablet = True
        try:
            self.tablet_service = ALProxy("ALTabletService")
        except:
            self.tablet = False
            
    def setAutonomousAbilities(self, blinking, background, awareness, listening, speaking):
        self.al.setAutonomousAbilityEnabled("AutonomousBlinking", blinking)
        self.al.setAutonomousAbilityEnabled("BackgroundMovement", background)
        self.al.setAutonomousAbilityEnabled("BasicAwareness", awareness)
        self.al.setAutonomousAbilityEnabled("ListeningMovement", listening)
        self.al.setAutonomousAbilityEnabled("SpeakingMovement", speaking)