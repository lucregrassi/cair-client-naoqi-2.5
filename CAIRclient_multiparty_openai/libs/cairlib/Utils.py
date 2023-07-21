"""
Authors:     Lucrezia Grassi (concept, design and code writing),
             Carmine Tommaso Recchiuto (concept and design),
             Antonio Sgorbissa (concept and design)
Email:       lucrezia.grassi@edu.unige.it
Affiliation: RICE, DIBRIS, University of Genoa, Italy

This file contains all the functions needed to retrieve information related to topics before starting the CAIR server
"""
import pickle
import random
import copy


class Utils:
    def __init__(self):
        pass

    def replace_schwa(self, sentence, speakers_info):
        # Loop over the elements of the list containing the pieces of the sentence along with their type to replace
        # names and, eventually, schwas
        for elem in sentence:
            gender = speakers_info[elem[2]]["gender"]
            if "$" in elem[1]:
                elem[1] = elem[1].replace("$" + elem[2], speakers_info[elem[2]]["name"])
            if "ə" in elem[1]:
                if gender == "f":
                    elem[1] = elem[1].replace("ə", "a")
                elif gender == "m":
                    elem[1] = elem[1].replace("ə", "o")
                else:
                    elem[1] = elem[1].replace("ə", "")
        return sentence

    def replace_schwa_in_string(self, sentence, speakers_info, current_speaker_id):
        if "ə" in sentence:
            if speakers_info[current_speaker_id]["gender"] == "f":
                schwa_replacement = "a"
            elif speakers_info[current_speaker_id]["gender"] == "m":
                schwa_replacement = "o"
            else:
                schwa_replacement = ""
            sentence = sentence.replace("ə", schwa_replacement)
        return sentence
            
    # From dialogue sentence as list of lists to string
    def compose_sentence(self, sentence_pieces):
        dialogue_sentence_str = ""
        for elem in sentence_pieces:
            if dialogue_sentence_str:
                dialogue_sentence_str = dialogue_sentence_str + " " + elem[1]
            else:
                dialogue_sentence_str = elem[1]
        return dialogue_sentence_str

    # This function trims any point, comma or parenthesis, and replaces underscores with spaces
    def clean_text(self, text):
        text = text.replace(',', '')
        text = text.replace('.', '')
        text = text.replace('(', '')
        text = text.replace(')', '')
        text = text.replace('_', ' ')
        text = text.lower()
        return text

    # This function chooses a topic from those passed as parameters, based on their likeliness
    def incremental_likeliness_based_choice(self, topics, likelinesses, allow_zero):
        valid_topics = []
        likelinesses_sum = 0.0
        incremental_likelinesses = []
        for i in range(len(topics)):
            # Pick topics with likeliness different from zero
            if float(likelinesses[topics[i]]) != 0.0:
                likelinesses_sum = likelinesses_sum + float(likelinesses[topics[i]])
                incremental_likelinesses.append(likelinesses_sum)
                valid_topics.append(topics[i])
        # If there are topics with likeliness != 0
        if valid_topics:
            # Initialize the chosen topic to the first valid one
            chosen_topic = valid_topics[0]
            print("Valid topics: ", valid_topics)
            print("Incremental likelinesses: ", incremental_likelinesses)
            rand_num = random.uniform(0.0, likelinesses_sum)
            print("Random number chosen:", rand_num)
            for n in range(len(incremental_likelinesses)):
                if incremental_likelinesses[n] < rand_num <= incremental_likelinesses[n + 1]:
                    chosen_topic = valid_topics[n + 1]
        # If there are no topics with likeliness != 0
        else:
            # If we can return topics with likeliness 0, choose one randomly
            if allow_zero:
                print("Choosing randomly among topics, even with likeliness 0")
                chosen_topic = random.choice(topics)
            # If we are not allow considering topics with likeliness 0, return -1
            else:
                chosen_topic = -1
        print("Chosen topic: ", chosen_topic)
        return chosen_topic

    def choose_next_topic(self, text, ontology, likelinesses):
        if text == " " or text == "_":
            text = "null"
        text = self.clean_text(text)

        # Find matches of parameters #1
        param1_topic_match = []
        keyword1 = []
        for param1 in ontology.req_par1:
            # Check each keyword contained in each list of requested_parameters_1
            for keyword in param1:
                # If the keyword is contained in the text return all topics that have that keyword as first parameter
                if keyword in text:
                    if keyword not in keyword1:
                        keyword1.append(keyword)
                    topics1 = [i for i, x in enumerate(ontology.req_par1) if x == param1]
                    for t in topics1:
                        if t not in param1_topic_match:
                            param1_topic_match.append(t)

        # If no keyword 1 is found - do not change topic
        if not keyword1:
            print("No keyword 1 found - return topic ", -1)
            return -1
        else:
            print("Keyword 1 found:", keyword1)

        # print("\nSecond parameters of those topics: ")
        topics_matching_both_keywords = []
        topics_matching_first_keyword = []
        keyword2 = []
        for n_topic in range(ontology.tot_topic):
            # Consider only the topics matching the first keyword
            if n_topic in param1_topic_match:
                # print(n_topic)
                # print(req_par2[n_topic])
                for keyword in ontology.req_par2[n_topic]:
                    if keyword in text or keyword == "*":
                        if keyword not in keyword2:
                            keyword2.append(keyword)
                        if keyword != "*":
                            if n_topic not in topics_matching_both_keywords:
                                topics_matching_both_keywords.append(n_topic)
                        else:
                            if n_topic not in topics_matching_first_keyword:
                                topics_matching_first_keyword.append(n_topic)

        # If no keyword 2 is found (neither an asterisk) - do not change topic
        if not keyword2:
            print("No keyword 2 found - return topic ", -1)
            return -1
        else:
            print("Keyword 2 found:", keyword2)

        double_matching_topics = []
        for n_topic in topics_matching_both_keywords:
            double_matching_topics.append(ontology.id_reqs[n_topic])
        print("Topics matching both keywords:", double_matching_topics)

        single_matching_topics = []
        for n_topic in topics_matching_first_keyword:
            single_matching_topics.append(ontology.id_reqs[n_topic])
        print("Topics matching only first keyword (and asterisk)", single_matching_topics)

        # When the function is called from here it means we are processing the user sentence, hence we allow returning
        # topics with likeliness zero, if there are no topics with likeliness different from zero.
        # Try choosing the next topic using topics matching two keywords, if present
        nxt_topic = -1
        if topics_matching_both_keywords:
            print("Choose among the topics matching both keywords")
            nxt_topic = self.incremental_likeliness_based_choice(topics_matching_both_keywords, likelinesses, True)
        # If no topic matches both keywords, try with those matching only the first keyword
        if nxt_topic == -1:
            if topics_matching_first_keyword:
                print("Choose among topics matching only first keyword")
                nxt_topic = self.incremental_likeliness_based_choice(topics_matching_first_keyword, likelinesses, True)
        return nxt_topic

    def choose_pattern(self, topic_n, topics_likeliness, ontology, provide_opinion):
        with open(ontology.folder_name + "/patterns.txt", 'rb') as file:
            patterns = pickle.load(file)

        print("Choosing pattern for topic ", topic_n)
        # If the likeliness is a value among 0 and 1 follow the pattern
        pattern = random.choice(patterns)

        # If the topic has likeliness 1 do not take questions into consideration
        if topics_likeliness[topic_n] == 1.0 or provide_opinion:
            print("Topic likeliness is 1 or user requested an opinion. "
                  "Delete question from pattern, and add a positive at the beginning.")
            pattern = [x for x in pattern if x != 'q']
            pattern.insert(0, 'p')
        sentence_type = pattern[0]
        prev_topic_pattern = copy.deepcopy(pattern[1:])

        print("NEW PATTERN CHOSEN!")
        print("Next sentence:", sentence_type)
        print("Following sentences:", prev_topic_pattern)
        return sentence_type, prev_topic_pattern

    def choose_sentence(self, sentence_type, topic_n, ontology, topic_sentences_flags, topic_likeliness):
        print("Choosing sentence of type: ", sentence_type)
        topic_sentences = ontology.topics_sentences[topic_n]
        topic_sentences_types = ontology.topics_sentences_types[topic_n]

        candidate_sentences = []
        no_sentences_of_that_type = True
        for t in range(len(topic_sentences_types)):
            # If the type of the sentence is the required one, and it has been not already said
            if topic_sentences_types[t] == sentence_type:
                no_sentences_of_that_type = False
                if topic_sentences_flags[t] == 0:
                    candidate_sentences.append(topic_sentences[t])
        # If there are candidate sentences to be said, choose one randomly, and set its flag to 1
        if candidate_sentences:
            print("There are sentences of the required type!")
            sentence = []
            chosen_sentence = random.choice(candidate_sentences)
            # If the sentence is a question...
            if sentence_type == 'q':
                # If the likeliness is not 0, once every 5 times add a common sentence of type q before the question
                # If the likeliness of the topic is zero, add a sentence before (containing the name of the prev speaker)
                if topic_likeliness == 0.0:
                    sentence.append(['zq', random.choice(ontology.common_sent_dict['zq'])])
                # Once every 5 times add a more complex bq, while all the other times, just add the most simple one (the
                # first one, which contains only the vocative (4 times over 5)
                if random.random() < 0.2:
                    # Append the question without the vocative after the bq sentence (that already contains it)
                    sentence.append(['bq', random.choice(ontology.common_sent_dict['bq'][1:])])
                else:
                    # If there is no sentence before the question, add the first bq sentence that contains only the vocative
                    sentence.append(['bq', ontology.common_sent_dict['bq'][0]])
                # In any case, add the question afterwards (without $desspk)
                sentence.append(['q', chosen_sentence])

            # If the sentence is w, g, or c, add a vocative before
            elif sentence_type == 'w' or sentence_type == 'g' or sentence_type == 'c':
                sentence.append([sentence_type, "$desspk " + chosen_sentence])
            # If the sentence type is p or n, add $prevspk before
            # TODO: if the topic had likeliness 1, the p is preceded by ka, hence $prevspk should not be added
            else:
                sentence.append([sentence_type, "$prevspk " + chosen_sentence])
            # Flag the chosen sentence
            for s in range(len(topic_sentences)):
                if topic_sentences[s] == chosen_sentence:
                    topic_sentences_flags[s] = 1
                    print("Flagged chosen sentence.")
            print("Chosen sentence: ", sentence)
            return sentence, topic_sentences_flags
        else:
            if no_sentences_of_that_type:
                print("No sentences of this type")
                return "", topic_sentences_flags
            else:
                print("No more candidate sentences! All flagged!")
                # Delete the flag from all the sentences of that type
                for t in range(len(topic_sentences_types)):
                    # If the type of the sentence is the required one, and it has been not already said
                    if topic_sentences_types[t] == sentence_type:
                        print("Unflag the sentence of type: ", sentence_type)
                        topic_sentences_flags[t] = 0
                # Call the function again with the all the flags set to zero
                return self.choose_sentence(sentence_type, topic_n, ontology, topic_sentences_flags, topic_likeliness)

    def explore_DT(self, dialogue_sentence, prev_topic_number, prev_topic_pattern, prev_topic_stop, ontology,
                   topics_likeliness, topics_sentences_flags, negative):
        # If the pattern is not finished, continue
        if prev_topic_pattern:
            print("Previous topic still has a pattern: ", prev_topic_pattern)
            sentence_type = prev_topic_pattern[0]
            try:
                prev_topic_pattern = prev_topic_pattern[1:]
            except:
                prev_topic_pattern = []
            print("Next sentence type: ", sentence_type)
            print("Next sentences type (updated): ", prev_topic_pattern)
            resp, topic_sentences_flags = self.choose_sentence(sentence_type, prev_topic_number, ontology,
                                                               topics_sentences_flags[prev_topic_number],
                                                               topics_likeliness[prev_topic_number])
            topics_sentences_flags[prev_topic_number] = topic_sentences_flags
            if not dialogue_sentence:
                dialogue_sentence = []
            # If there is a sentence of the required type, add the tuples to the dialogue sentence
            if resp:
                print("Old dialogue sentence*:", dialogue_sentence)
                for t in resp:
                    dialogue_sentence.append(t)
                print("New dialogue sentence*:", dialogue_sentence)
            # If there is no sentence of that type for that topic, continue with the pattern
            else:
                print("No sentence of type", sentence_type, "available, continue with the pattern.")
                prev_topic_pattern = prev_topic_pattern[1:]
                return self.explore_DT(dialogue_sentence, prev_topic_number, prev_topic_pattern, prev_topic_stop,
                                       ontology,
                                       topics_likeliness, topics_sentences_flags, False)
            topic_n = prev_topic_number
        # If the pattern is finished, choose among children - descend the tree
        else:
            print("** EMPTY PATTERN **")
            # TODO: this has to be fixed because it should not happen, this is a quick fix to avoid errors
            # prev_topic_number should never be -1
            if prev_topic_number != -1:
                # The user answered no
                if negative:
                    # If the user said no twice
                    if prev_topic_stop:
                        # Do not allow choosing father's brothers with likeliness zero
                        # topic_n = choose_topic(topics_brothers[topics_father[prev_topic_number]], topics_likeliness, False)
                        # Do not jump further - end conversation
                        topic_n = -1
                        prev_topic_stop = False
                        # print("Second NEGATIVE answer: CHOOSE NEW TOPIC AMONG FATHER's BROTHERS")
                        print("Second NEGATIVE answer: END CONVERSATION")
                    else:
                        # Do not allow choosing brothers with likeliness zero
                        topic_n = self.incremental_likeliness_based_choice(ontology.topics_brothers[prev_topic_number],
                                                                           topics_likeliness, False)
                        prev_topic_stop = True
                        print("First NEGATIVE answer: CHOOSE NEW TOPIC AMONG BROTHERS")
                else:
                    # Do not allow choosing children with likeliness zero
                    topic_n = self.incremental_likeliness_based_choice(ontology.topics_children[prev_topic_number],
                                                                       topics_likeliness, False)
                    print("** DESCEND THE DT: CHOOSE NEW TOPIC AMONG CHILDREN")
            else:
                # set topic_n to -1
                topic_n = prev_topic_number
            # If there are children/brothers with likeliness != 0, jump to one of them
            if topic_n != -1:
                prev_topic_number = topic_n
                sentence_type, prev_topic_pattern = self.choose_pattern(topic_n, topics_likeliness, ontology, False)
                resp, topic_sentences_flags = self.choose_sentence(sentence_type, topic_n, ontology,
                                                                   topics_sentences_flags[topic_n],
                                                                   topics_likeliness[topic_n])
                topics_sentences_flags[topic_n] = topic_sentences_flags
                if not dialogue_sentence:
                    dialogue_sentence = []
                # If there is a sentence of the required type, add the tuples to the dialogue sentence
                if resp:
                    print("Old dialogue sentence: ", dialogue_sentence)
                    for t in resp:
                        dialogue_sentence.append(t)
                    print("New dialogue sentence: ", dialogue_sentence)
            # If there are no children/brothers or no children/brothers with likeliness != 0
            else:
                top_concept = False
                brother = False
                print("No children/brothers (one no)/father's brothers (two no) - or none with non zero likeliness")
                rand_n = random.uniform(0.0, 1.0)
                print("Random number to decide what to do:", rand_n)

                if rand_n < 0.1:
                    print("** CHOOSING AMONG BROTHERS with likeliness different from zero")
                    brother = True
                    topic_n = self.incremental_likeliness_based_choice(ontology.topics_brothers[prev_topic_number],
                                                                  topics_likeliness, False)
                elif 0.1 <= rand_n < 0.45:
                    print("** CHOOSING AMONG TOP CONCEPTS with likeliness different from zero")
                    top_concept = True
                    topic_n = self.incremental_likeliness_based_choice(ontology.top_topics, topics_likeliness, False)
                if topic_n != -1:
                    print("A valid topic has been found! Jump to that")
                    prev_topic_number = topic_n
                    sentence_type, prev_topic_pattern = self.choose_pattern(topic_n, topics_likeliness, ontology, False)
                    resp, topic_sentences_flags = self.choose_sentence(sentence_type, topic_n, ontology,
                                                                       topics_sentences_flags[topic_n],
                                                                       topics_likeliness[topic_n])
                    topics_sentences_flags[topic_n] = topic_sentences_flags
                    if not dialogue_sentence:
                        dialogue_sentence = []
                    # If there is a sentence of the required type, add the tuples to the dialogue sentence
                    if resp:
                        print("Old dialogue sentence: ", dialogue_sentence)
                        if top_concept:
                            dialogue_sentence.append(['et', random.choice(ontology.common_sent_dict['et'])])
                        if brother:
                            dialogue_sentence.append(['eb', random.choice(ontology.common_sent_dict['eb'])])
                        for t in resp:
                            dialogue_sentence.append(t)
                        print("New dialogue sentence: ", dialogue_sentence)
                # Random number is between 0.45 and 1 - or there are no brothers/top concepts with l != 0
                else:
                    print("** FINAL SENTENCE")
                    topic_n = prev_topic_number
                    sentence_type = 'e'
                    prev_topic_pattern = []
                    # The end sentence already contains the vocative.
                    dialogue_sentence.append(['e', random.choice(ontology.common_sent_dict['e'])])

        # If the sentence is positive or negative, call this function again to go on with the pattern
        if sentence_type == 'p':
            # prev_topic_pattern = prev_topic_pattern[1:]
            print("POSITIVE sentence, update the pattern to: ", prev_topic_pattern)
            return self.explore_DT(dialogue_sentence, prev_topic_number, prev_topic_pattern, prev_topic_stop, ontology,
                                   topics_likeliness, topics_sentences_flags, False)
        if sentence_type == 'n':
            print("NEGATIVE sentence")
            return self.explore_DT(dialogue_sentence, prev_topic_number, prev_topic_pattern, prev_topic_stop, ontology,
                                   topics_likeliness, topics_sentences_flags, True)

        return sentence_type, prev_topic_pattern, dialogue_sentence, topic_n, prev_topic_stop, topics_sentences_flags

    # This function explores the DT based on the pattern. If the pattern is empty (the current topic is over), this 
    # function chooses a new topic and a new pattern for the topic (always starting with a question)
    def explore_DT_openai(self, prev_topic_number, prev_topic_pattern, prev_topic_stop, ontology, topics_likeliness, negative):
        print("Prev topic number:", prev_topic_number)
        # If the pattern is not finished, continue
        if prev_topic_pattern:
            print("Previous topic still has a pattern: ", prev_topic_pattern)
            sentence_type = prev_topic_pattern[0]
            try:
                prev_topic_pattern = prev_topic_pattern[1:]
            except:
                prev_topic_pattern = []
            print("Next sentence type: ", sentence_type)
            print("Next sentences type (updated): ", prev_topic_pattern)
            topic_n = prev_topic_number
        # If the pattern is finished, choose among children - descend the tree
        else:
            print("** EMPTY PATTERN **")
            # The user answered no
            if negative:
                # If the user said no twice
                if prev_topic_stop:
                    # Do not allow choosing father's brothers with likeliness zero
                    # topic_n = choose_topic(topics_brothers[topics_father[prev_topic_number]], topics_likeliness, False)
                    # Do not jump further - end conversation
                    topic_n = -1
                    prev_topic_stop = False
                    # print("Second NEGATIVE answer: CHOOSE NEW TOPIC AMONG FATHER's BROTHERS")
                    print("Second NEGATIVE answer: END CONVERSATION")
                else:
                    # Do not allow choosing brothers with likeliness zero
                    topic_n = self.incremental_likeliness_based_choice(ontology.topics_brothers[prev_topic_number],
                                                                       topics_likeliness, False)
                    prev_topic_stop = True
                    print("First NEGATIVE answer: CHOOSE NEW TOPIC AMONG BROTHERS")
            else:
                # Do not allow choosing children with likeliness zero
                topic_n = self.incremental_likeliness_based_choice(ontology.topics_children[prev_topic_number],
                                                                   topics_likeliness, False)
                print("** DESCEND THE DT: CHOOSE NEW TOPIC AMONG CHILDREN")

            # If there are children/brothers with likeliness != 0, jump to one of them
            if topic_n != -1:
                prev_topic_number = topic_n
                sentence_type, prev_topic_pattern = self.choose_pattern(topic_n, topics_likeliness, ontology, False)
            # If there are no children/brothers or no children/brothers with likeliness != 0
            else:
                top_concept = False
                brother = False
                print("No children/brothers (one no)/father's brothers (two no) - or none with non zero likeliness")
                rand_n = random.uniform(0.0, 1.0)
                print("Random number to decide what to do:", rand_n)

                if rand_n < 0.1:
                    print("** CHOOSING AMONG BROTHERS with likeliness different from zero")
                    brother = True
                    topic_n = self.incremental_likeliness_based_choice(ontology.topics_brothers[prev_topic_number],
                                                                  topics_likeliness, False)
                elif 0.1 <= rand_n < 0.45:
                    print("** CHOOSING AMONG TOP CONCEPTS with likeliness different from zero")
                    top_concept = True
                    topic_n = self.incremental_likeliness_based_choice(ontology.top_topics, topics_likeliness, False)
                if topic_n != -1:
                    print("A valid topic has been found! Jump to that")
                    prev_topic_number = topic_n
                    sentence_type, prev_topic_pattern = self.choose_pattern(topic_n, topics_likeliness, ontology, False)
                # Random number is between 0.45 and 1 - or there are no brothers/top concepts with l != 0
                else:
                    print("** FINAL SENTENCE")
                    topic_n = prev_topic_number
                    sentence_type = 'e'
                    prev_topic_pattern = []

        return sentence_type, prev_topic_pattern, topic_n, prev_topic_stop
    
    def start_new_pattern(self, topic_n, prev_topic_stop, ontology, topics_likeliness, topics_sentences_flags,
                          provide_opinion):
        sentence_type, prev_topic_pattern = self.choose_pattern(topic_n, topics_likeliness, ontology, provide_opinion)
        print("Chosen pattern of new topic: ", sentence_type, prev_topic_pattern)
        dialogue_sentence, topic_sentences_flags = self.choose_sentence(sentence_type, topic_n, ontology,
                                                                        topics_sentences_flags[topic_n],
                                                                        topics_likeliness[topic_n])
        topics_sentences_flags[topic_n] = topic_sentences_flags

        # If no initial sentence has been chosen, or the sentence is p because the topic likeliness is already 1, explore
        # the DT until the sentence type is q, w, or c
        while not dialogue_sentence or sentence_type == 'p':
            sentence_type, prev_topic_pattern, dialogue_sentence, topic_n, prev_topic_stop, topics_sentences_flags = \
                self.explore_DT(dialogue_sentence, topic_n, prev_topic_pattern, prev_topic_stop, ontology,
                                topics_likeliness,
                                topics_sentences_flags, False)

        return sentence_type, prev_topic_pattern, dialogue_sentence, topic_n, prev_topic_stop, topics_sentences_flags
