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

