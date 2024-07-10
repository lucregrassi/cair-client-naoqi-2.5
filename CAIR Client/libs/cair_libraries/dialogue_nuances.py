"""
Authors:     Lucrezia Grassi (concept, design and code writing),
             Carmine Tommaso Recchiuto (concept and design),
             Antonio Sgorbissa (concept and design)
Email:       lucrezia.grassi@edu.unige.it
Affiliation: RICE, DIBRIS, University of Genoa, Italy

This file contains the class DialogueNuances modelling the nuances used with LLMs
"""
import time
import numpy as np
import random


class DialogueNuances:
    def __init__(self, nuance_matrices=None, nuance_vectors=None):
        self.nuances = ["diversity", "time", "place", "tone", "positive_speech_act", "contextual_speech_act"]
        # Diversity
        self.diversity_matrix = np.array(nuance_matrices["diversity"])
        self.diversity_flags = np.array(nuance_vectors["flags"]["diversity"])
        self.diversity_values = nuance_vectors["values"]["diversity"]
        self.diversity_fields = ["nationality", "mental condition", "physical condition"]
        # Time
        self.time_matrix = np.array(nuance_matrices["time"])
        self.time_flags = np.array(nuance_vectors["flags"]["time"])
        self.time_values = nuance_vectors["values"]["time"]
        self.time_fields = ["timeofday", "season", "events"]
        # Place
        self.place_matrix = np.array(nuance_matrices["place"])
        self.place_flags = np.array(nuance_vectors["flags"]["place"])
        self.place_values = nuance_vectors["values"]["place"]
        self.place_fields = ["environment", "city", "nation"]
        # Tone
        self.tone_matrix = np.array(nuance_matrices["tone"])
        self.tone_flags = np.array(nuance_vectors["flags"]["tone"])
        self.tone_values = nuance_vectors["values"]["tone"]
        # Positive speech act
        self.positive_speech_act_matrix = np.array(nuance_matrices["positive_speech_act"])
        self.positive_speech_act_flags = np.array(nuance_vectors["flags"]["positive_speech_act"])
        self.positive_speech_act_values = nuance_vectors["values"]["positive_speech_act"]
        # Contextual speech act
        self.contextual_speech_act_matrix = np.array(nuance_matrices["contextual_speech_act"])
        self.contextual_speech_act_flags = np.array(nuance_vectors["flags"]["contextual_speech_act"])
        self.contextual_speech_act_values = nuance_vectors["values"]["contextual_speech_act"]
        random.seed(time.time())

    def from_probabilities_to_flags(self, probabilities):
        updated_flags = np.zeros(len(probabilities))
        rand_num = random.uniform(0.0, 1.0)
        incremental_sum = 0.0
        one_index = 0
        for n in range(len(probabilities)):
            incremental_sum = incremental_sum + probabilities[n]
            if rand_num <= incremental_sum:
                one_index = n
                break
        for i in range(len(updated_flags)):
            if i == one_index:
                updated_flags[i] = 1
            else:
                updated_flags[i] = 0
        return updated_flags

    def update_flags(self):
        # Diversity
        diversity_probabilities = self.diversity_matrix.dot(self.diversity_flags)
        self.diversity_flags = self.from_probabilities_to_flags(diversity_probabilities)
        # Time
        time_probabilities = self.time_matrix.dot(self.time_flags)
        self.time_flags = self.from_probabilities_to_flags(time_probabilities)
        # Place
        place_probabilities = self.place_matrix.dot(self.place_flags)
        self.place_flags = self.from_probabilities_to_flags(place_probabilities)
        # Tone
        tone_probabilities = self.tone_matrix.dot(self.tone_flags)
        self.tone_flags = self.from_probabilities_to_flags(tone_probabilities)
        # Positive speech act
        positive_speech_act_probabilities = self.positive_speech_act_matrix.dot(self.positive_speech_act_flags)
        self.positive_speech_act_flags = self.from_probabilities_to_flags(positive_speech_act_probabilities)
        # Contextual speech act
        contextual_speech_act_probabilities = self.contextual_speech_act_matrix.dot(self.contextual_speech_act_flags)
        self.contextual_speech_act_flags = self.from_probabilities_to_flags(contextual_speech_act_probabilities)

    def to_dictionary(self):
        return {"flags": {"diversity": self.diversity_flags.astype(int).tolist(),
                          "time": self.time_flags.astype(int).tolist(),
                          "place": self.place_flags.astype(int).tolist(),
                          "tone": self.tone_flags.astype(int).tolist(),
                          "positive_speech_act": self.positive_speech_act_flags.astype(int).tolist(),
                          "contextual_speech_act": self.contextual_speech_act_flags.astype(int).tolist()
                          },
                "values": {"diversity": self.diversity_values,
                           "time": self.time_values,
                           "place": self.place_values,
                           "tone": self.tone_values,
                           "positive_speech_act": self.positive_speech_act_values,
                           "contextual_speech_act": self.contextual_speech_act_values
                           }
                }

    def nuance_sentences(self):
        nuance_sentences_dict = {}
        for elem in self.nuances:
            if elem == "diversity":
                i = np.where(self.diversity_flags == 1.0)[0][0]
                if i == len(self.diversity_flags) - 1:
                    nuance_sentences_dict["diversity"] = "Optional: information about " \
                                                     "the person you are interacting with: [" + ', '.join(self.diversity_values) + "]."
                else:
                    # Compulsory
                    nuance_sentences_dict["diversity"] = "Optional: the person you are interacting with is " + \
                                                         self.diversity_values[i] + "."
            elif elem == "time":
                i = np.where(self.time_flags == 1.0)[0][0]
                if i == len(self.time_flags) - 1:
                    nuance_sentences_dict["time"] = "Optional: information about the moment in which the "\
                                                    "conversation is happening: [" + ', '.join(self.time_values) + "]."
                else:
                    # Compulsory
                    nuance_sentences_dict["time"] = "Optional: the conversation is taking place during the " + self.time_values[i] + "."
            elif elem == "place":
                i = np.where(self.place_flags == 1.0)[0][0]
                if i == len(self.place_flags) - 1:
                    nuance_sentences_dict["place"] = "Optional: information about the place in which the " \
                                                "conversation is happening: [" + ', '.join(self.place_values) + "]."
                else:
                    # Compulsory
                    nuance_sentences_dict["place"] = "Optional: the conversation is taking place in " + self.place_values[i] + "."
            elif elem == "tone":
                i = np.where(self.tone_flags == 1.0)[0][0]
                if i == len(self.tone_flags) - 1:
                    nuance_sentences_dict["tone"] = "Compulsory: you have to use a " + self.tone_values[i] + " tone."
                else:
                    nuance_sentences_dict["tone"] = "Compulsory: you have to use a " + self.tone_values[i] + " tone."
            elif elem == "positive_speech_act":
                i = np.where(self.positive_speech_act_flags == 1.0)[0][0]
                if i == len(self.positive_speech_act_flags) - 1:
                    nuance_sentences_dict["positive_speech_act"] = "You can use one of the speech acts among the following: " \
                                                                + ', '.join(self.positive_speech_act_values) + " "
                else:
                    nuance_sentences_dict["positive_speech_act"] = "If you want, you can use the " + \
                                                                   self.positive_speech_act_values[i] + " speech act "
            elif elem == "contextual_speech_act":
                i = np.where(self.contextual_speech_act_flags == 1.0)[0][0]
                if i == len(self.contextual_speech_act_flags) - 1:
                    nuance_sentences_dict["contextual_speech_act"] = "You can use one of the speech acts among the "\
                                                                      "following: " + ', '.join(self.contextual_speech_act_values) + " "
                else:
                    nuance_sentences_dict["contextual_speech_act"] = "If you want, you can use the " + \
                                                                     self.contextual_speech_act_values[i] + " speech act "
        return nuance_sentences_dict

