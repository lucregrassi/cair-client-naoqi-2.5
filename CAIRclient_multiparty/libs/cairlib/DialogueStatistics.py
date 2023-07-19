import numpy
import numpy as np
import copy

moving_window_time = 5 * 60
community_turns = 20


class DialogueStatistics:
    def __init__(self, profile_id=None, d=None):
        if profile_id:
            # Mapping between indexes of the matrices/vectors and the id of the speaker
            self.mapping_index_speaker = [profile_id]
            # Matrix containing who talked after who in the same turn
            self.same_turn = [[0]]
            # Matrix containing who talked after who in successive turns
            self.successive_turn = [[0]]
            # Matrix containing the average topic distance between two speakers
            self.average_topic_distance = [[0.0]]
            # Total number of turns for each speaker
            self.speakers_turns = [0]
            # A priori probability that a speaker talks
            self.a_priori_prob = [0.0]
            # Moving window containing the information about the turns in the last n minutes
            self.moving_window = []
            # List of IDs of the last m speakers who talked (used to identify communities)
            self.latest_turns = []
        if d:
            self.__dict__ = copy.deepcopy(d)

    # This method transforms the object in a dictionary and returns a deep copy of it
    def to_dict(self):
        dialogue_statistics_dict = copy.deepcopy(self.__dict__)
        return dialogue_statistics_dict

    # This method updates the statistics based on who spoke in the last turn
    def update_statistics(self, dialogue_turn, prev_turn_last_speaker):
        for i, turn_piece in enumerate(dialogue_turn.turn_pieces):
            profile_id = turn_piece.profile_id
            # Do not consider generic user in the moving window
            if profile_id != "00000000-0000-0000-0000-000000000000":
                if self.moving_window:
                    time = self.get_moving_window_total_time()
                    while (time + float(turn_piece.speaking_time) - float(self.moving_window[0]["speaking_time"])) > \
                            moving_window_time:
                        # Remove first element from the moving window
                        self.moving_window.pop(0)
                        time = self.get_moving_window_total_time()
                # Transform the turn piece to a dictionary and remove the sentence field as it is useless for statistics
                turn_piece_dict = turn_piece.to_dict()
                del turn_piece_dict["sentence"]
                self.moving_window.append(turn_piece_dict)
            # Increase the number of times that the previous speaker said something (including unknown speaker)
            speaker_index = self.mapping_index_speaker.index(profile_id)
            n_turns = self.speakers_turns[speaker_index]
            self.speakers_turns[speaker_index] = n_turns + 1
            # Ensure that the length of the latest turns array does not exceed the maximum one
            while len(self.latest_turns) > community_turns:
                self.latest_turns.pop(0)
            # Add the id of the last speaker at the end of the list
            self.latest_turns.append(profile_id)

            # If it's the first speaker of the turn (and it is not the first interaction),
            # check if the speaker is the same as the last one of the previous turn
            if i == 0:
                if prev_turn_last_speaker != "":
                    # Increment the element of the "successive_interaction" matrix with the indexes mapped to
                    # row = prev_interaction_last_speaker, column = profile_id
                    row = self.mapping_index_speaker.index(prev_turn_last_speaker)
                    column = self.mapping_index_speaker.index(profile_id)
                    old_value = self.successive_turn[row][column]
                    self.successive_turn[row][column] = old_value + 1
            else:
                # Increment the element of the "same_interaction" matrix with th indexes mapped to
                # row = same_interaction_last_speaker, column = profile_id
                row = self.mapping_index_speaker.index(dialogue_turn.turn_pieces[i - 1].profile_id)
                column = self.mapping_index_speaker.index(profile_id)
                old_value = self.same_turn[row][column]
                self.same_turn[row][column] = old_value + 1

        # Compute the total number of turns of all users
        tot_turns = 0
        for elem in self.speakers_turns:
            tot_turns = tot_turns + elem

        # Recompute all the a priori probabilities with the updated number of turns
        for i in range(len(self.mapping_index_speaker)):
            # Get the number of turns of that user
            speaker_turns = self.speakers_turns[i]
            # Compute the a priori probability and update the value in the array
            self.a_priori_prob[i] = float(speaker_turns) / float(tot_turns)

    # This method increases the size of a specific matrix, passed as a parameter
    def increase_matrix_size(self, matrix, value_type):
        # The dimension of the square matrix coincides with the length of the array containing the profile ids
        matrix_size = len(self.mapping_index_speaker)
        matrix = np.array(matrix)
        matrix = np.insert(matrix, matrix_size, np.zeros(matrix_size, dtype=value_type), axis=0)
        matrix = np.insert(matrix, matrix_size, np.zeros(matrix_size + 1, dtype=value_type), axis=1)
        return matrix.tolist()

    # This method updates the dialogue statistics when a new user performs the registration
    def add_new_speaker_statistics(self, profile_id):
        # For each element in the speakers_stats dictionary, add the new elements
        self.same_turn = self.increase_matrix_size(self.same_turn, int)
        self.successive_turn = self.increase_matrix_size(self.successive_turn, int)
        self.average_topic_distance = self.increase_matrix_size(self.average_topic_distance, float)
        self.mapping_index_speaker.append(profile_id)
        self.speakers_turns.append(0)
        self.a_priori_prob.append(0.0)

    # This method returns the total number of turns of the users from the beginning of the dialogue
    def get_total_turns(self):
        total_turns = 0
        for elem in self.speakers_turns:
            total_turns = total_turns + int(elem)
        return total_turns

    def get_registered_speakers_turns(self):
        registered_speakers_turns = 0
        if len(self.speakers_turns) > 1:
            for elem in self.speakers_turns[1:]:
                registered_speakers_turns = registered_speakers_turns + int(elem)
        return registered_speakers_turns

    def update_average_topic_distance(self, prev_speaker_id, prev_speaker_topic, current_speaker_id,
                                      current_speaker_topic, ontology):
        # Compute the distance between the new conversation topic of the speaker who talked now and the conversation
        # topic of the previous speaker - update the matrix before sending it back to the client
        row = self.mapping_index_speaker.index(prev_speaker_id)
        col = self.mapping_index_speaker.index(current_speaker_id)
        successive_turns = self.successive_turn[row][col]

        # Compute the distance between the two topics
        topic_distance = ontology.distance_between_two_topics(prev_speaker_topic, current_speaker_topic)
        print("Distance from previous topic:", topic_distance)
        # Previous average topic distance of the two speakers
        prev_avg_topic_distance = self.average_topic_distance[row][col]
        # Update average topic distance by multiplying the previous average for the number of successive turns
        # minus one, then adding the computed topic distance, and dividing for the number of successive turns
        self.average_topic_distance[row][col] = \
            ((prev_avg_topic_distance * (successive_turns - 1)) + topic_distance) / successive_turns

    # This method returns the number of times a specific speaker has spoken in the moving window
    def get_moving_window_speaker_turns(self, profile_id):
        speaker_turns = 0
        for elem in self.moving_window:
            if elem["profile_id"] == profile_id:
                speaker_turns = speaker_turns + 1
        return speaker_turns

    # This method returns the number of words said by a specific speaker in the moving window
    def get_moving_window_speaker_words(self, profile_id):
        speaker_words = 0
        for elem in self.moving_window:
            if elem["profile_id"] == profile_id:
                speaker_words = speaker_words + int(elem["number_of_words"])
        return speaker_words

    # This method returns the speaking time of a specific speaker in the moving window
    def get_moving_window_speaker_time(self, profile_id):
        speaker_time = 0.0
        for elem in self.moving_window:
            if elem["profile_id"] == profile_id:
                speaker_time = speaker_time + float(elem["speaking_time"])
        return speaker_time

    # This method returns the sum of the times of the pieces of turn in the moving window
    def get_moving_window_total_time(self):
        total_time = 0.0
        for elem in self.moving_window:
            total_time = total_time + float(elem["speaking_time"])
        return total_time

    # This method returns the sum of the number of words in the pieces of turn in the moving window
    def get_moving_window_total_words(self):
        total_words = 0
        for elem in self.moving_window:
            total_words = total_words + int(elem["number_of_words"])
        return total_words

    # This method returns the ratio between the speaking time of a speaker and the total speaking time in the moving
    # window, for all the speakers registered (excluding the unknown speaker)
    def get_speaking_time_ratio(self):
        speaking_time_ratio = []
        total_time = self.get_moving_window_total_time()
        for profile_id in self.mapping_index_speaker[1:]:
            speaker_time = self.get_moving_window_speaker_time(profile_id)
            speaking_time_ratio.append(speaker_time / total_time)
        return speaking_time_ratio

    # This method returns the ratio between the number of words of a speaker and the total number of words in the moving
    # window, for all the speakers registered (excluding the unknown speaker)
    def get_number_of_words_ratio(self):
        number_of_words_ratio = []
        total_words = self.get_moving_window_total_words()
        for profile_id in self.mapping_index_speaker[1:]:
            speaker_words = self.get_moving_window_speaker_words(profile_id)
            number_of_words_ratio.append(speaker_words / total_words)
        return number_of_words_ratio

    # This method returns the matrix containing successive turns in the latest turns (called in community detector)
    def get_latest_turns_successive_turn_matrix(self):
        matrix_size = len(self.mapping_index_speaker)
        # Initialize the matrix to the correct size and fill it with zeros
        successive_turn = np.zeros((matrix_size, matrix_size))
        # Increase the number of successive turns of the users in the latest turns
        for i, speaker_id in enumerate(self.latest_turns):
            # Do it only if it is not the first element
            if i != 0:
                speaker_index = self.mapping_index_speaker.index(speaker_id)
                prev_speaker_index = self.mapping_index_speaker.index(self.latest_turns[i-1])
                successive_turn[prev_speaker_index][speaker_index] = \
                    successive_turn[prev_speaker_index][speaker_index] + 1
        return successive_turn
