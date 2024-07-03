"""
Authors:     Lucrezia Grassi (concept, design and code writing),
             Carmine Tommaso Recchiuto (concept and design),
             Antonio Sgorbissa (concept and design)
Email:       lucrezia.grassi@edu.unige.it
Affiliation: RICE, DIBRIS, University of Genoa, Italy

This file contains the class SpeakerInfo modelling the information of each registered speaker
"""
import copy


class SpeakerInfo:
    def __init__(self, profile_id=None, name=None, gender=None, age=None, d=None):
        if profile_id:
            self.profile_id = profile_id
            self.name = name
            self.gender = gender
            self.age = age
        if d:
            self.__dict__ = copy.deepcopy(d)

    def to_dict(self):
        speaker_info_dict = copy.deepcopy(self.__dict__)
        return speaker_info_dict

