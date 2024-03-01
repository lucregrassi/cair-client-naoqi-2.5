"""
Authors:     Lucrezia Grassi (concept, design and code writing),
             Carmine Tommaso Recchiuto (concept and design),
             Antonio Sgorbissa (concept and design)
Email:       lucrezia.grassi@edu.unige.it
Affiliation: RICE, DIBRIS, University of Genoa, Italy

This file contains the class DialogueSentencePiece modelling a piece of sentence
"""


class DialogueSentencePiece:
    def __init__(self, sentence_type=None, sentence=None, profile_id=None):
        self.sentence_type = sentence_type
        self.sentence = sentence
        self.profile_id = profile_id
