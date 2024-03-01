"""
Authors:     Lucrezia Grassi (concept, design and code writing),
             Carmine Tommaso Recchiuto (concept and design),
             Antonio Sgorbissa (concept and design)
Email:       lucrezia.grassi@edu.unige.it
Affiliation: RICE, DIBRIS, University of Genoa, Italy

This file contains the class DialogueState modelling the state of the dialogue
"""
import copy


class DialogueState:
    def __init__(self, d=None):
        self.dialogue_sentence = None
        self.prev_dialogue_sentence = None
        self.addressed_speaker = None
        self.topic = None
        self.prev_topic = None
        self.sentence_type = None
        self.pattern = None
        self.bool = None
        self.likelinesses = None
        self.flags = None
        self.addressed_community = None
        self.dialogue_nuances = None
        self.conversation_history = None
        self.__dict__ = copy.deepcopy(d)

    def to_dict(self):
        dialogue_state_dict = copy.deepcopy(self.__dict__)
        return dialogue_state_dict
