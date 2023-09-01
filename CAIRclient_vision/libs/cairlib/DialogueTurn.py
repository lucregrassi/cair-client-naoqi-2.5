import copy
import xml.etree.ElementTree as ET


class TurnPiece:
    """
        Models a piece of dialogue turn.

        Attributes
        ----------
        profile_id : string
            The profile id of the speaker.
        sentence : str
            The sentence said by the speaker
        speaking_time : float
            The duration in seconds of the sentences
        number_of_words : int
            The number of words contained in the sentence

        Methods
        -------
        to_dict()
            Converts the object to a dictionary
        """
    def __init__(self, profile_id, sentence, speaking_time):
        """
        Parameters
        ----------
        profile_id : str
            The profile id of the speaker.
        sentence : str, optional
            The sentence said by the speaker
        speaking_time : int
            The duration in seconds of the sentences
        """
        self.profile_id = profile_id
        self.sentence = sentence
        self.speaking_time = speaking_time
        self.number_of_words = len(self.sentence.split())

    def to_dict(self):
        """
        Transforms the object in a dictionary

        Returns
        -------
        dict
            A dictionary containing as keys the name of the attributes and as values their value
        """
        turn_piece_dict = copy.deepcopy(self.__dict__)
        return turn_piece_dict


# This class models a dialogue turn, formed by many turn pieces.
# It is possible to create an empty turn or generate a dialogue turn object starting from a xml string
class DialogueTurn:
    def __init__(self, xml_string=None, d=None):
        self.turn_pieces = []
        if xml_string:
            tree = ET.ElementTree(ET.fromstring(xml_string))
            profile_id_tags = tree.findall('profile_id')
            for i in range(len(profile_id_tags)):
                profile_id = profile_id_tags[i].attrib["value"]
                sentence = profile_id_tags[i].text
                speaking_time = profile_id_tags[i].find("speaking_time").text
                turn_piece = TurnPiece(profile_id, sentence, speaking_time)
                self.add_turn_piece(turn_piece)
        if d:
            self.__dict__ = copy.deepcopy(d)
            self.turn_pieces = []
            for piece in d["turn_pieces"]:
                # recreate the TurnPiece objects
                self.turn_pieces.append(TurnPiece(piece["profile_id"], piece["sentence"], piece["speaking_time"]))

    def to_xml_string(self):
        root = ET.Element("response")
        for turn_piece in self.turn_pieces:
            profile_id = turn_piece.profile_id
            sentence = turn_piece.sentence
            speaking_time = turn_piece.speaking_time
            profile_id_tag = ET.SubElement(root, "profile_id", value=profile_id)
            profile_id_tag.text = sentence
            ET.SubElement(profile_id_tag, "speaking_time").text = str(speaking_time)
        return ET.tostring(root, encoding='unicode')

    def to_dict(self):
        dialogue_turn_dict = copy.deepcopy(self.__dict__)
        turn_pieces_dict_list = []
        for piece in self.turn_pieces:
            turn_pieces_dict_list.append(piece.to_dict())
        dialogue_turn_dict["turn_pieces"] = copy.deepcopy(turn_pieces_dict_list)
        return dialogue_turn_dict

    # Returns a string containing just the plain text of the turn
    def get_text(self):
        sentence = ""
        for turn_piece in self.turn_pieces:
            sentence = sentence + " " + turn_piece.sentence
        return sentence

    # This method checks if the dialogue turn contains at least one piece
    def is_empty(self):
        if self.turn_pieces:
            return False
        else:
            return True

    # This method adds a turn piece to the dialogue turn (or it modifies the last one if the speaker is the same)
    def add_turn_piece(self, turn_piece):
        # If the list of turn pieces is not empty, check that the new turn piece does not belong to the same speaker
        if self.turn_pieces:
            # Check if the profile id is always the same one
            if turn_piece.profile_id == self.turn_pieces[-1].profile_id:
                # Append the transcribed string to the text of the last profile id
                self.turn_pieces[-1].sentence = self.turn_pieces[-1].sentence + " " + turn_piece.sentence
                self.turn_pieces[-1].speaking_time = self.turn_pieces[-1].speaking_time + turn_piece.speaking_time
            # If the id has changed, add a new element
            else:
                self.turn_pieces.append(turn_piece)
        # If there are no turn pieces, add the first one
        else:
            self.turn_pieces.append(turn_piece)

    def get_turn_speaking_time(self):
        speaking_time = 0.0
        for piece in self.turn_pieces:
            speaking_time = speaking_time + float(piece.speaking_time)
        return speaking_time




