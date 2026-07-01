# -*- coding: utf-8 -*-
"""
Functions for syntactic measures literallily copied from Terčon 2024, https://github.com/lukatercon/SyntComplex
"""

import math


#####
# Measures from Terčon 2004 start here
#####

# mean dependency distance function
def mdd(sentence):
    list_of_dd = list()
    for tok in sentence:
        if tok["deprel"] not in ["punct", "root"]:
            list_of_dd.append(abs(int(tok["id"]) - int(tok["head"])))

    return sum(list_of_dd)/len(list_of_dd) if len(list_of_dd) > 0 else "n/a"


# normalized dependencies distance function
def ndd(sentence):
    sent_mdd = mdd(sentence)
    if sent_mdd == "n/a":
        return "n/a"

    root_distance = 0
    sentence_length = 0
    for tok in sentence:
        if tok["deprel"] == "root":
            root_distance = int(tok["id"])

        if tok["deprel"] not in ["punct", "root"]:
            sentence_length += 1

    if root_distance < 1 or sentence_length < 1:
        raise Exception(f"ERROR: either root_distance or sentence_length could not be"
                        f"set in {sentence.metadata['sent_id']}")

    return abs(math.log(sent_mdd / math.sqrt(root_distance * sentence_length)))


# maximum tree depth function
def max_tree_depth(sentence):
    depths_list = list()
    for tok in sentence:
        tok_depth = 1
        next_head = tok["head"]
        while next_head != 0:
            tok_depth += 1
            next_head = sentence[int(next_head) - 1]["head"]

        depths_list.append(tok_depth)

    return max(depths_list)


def has_cop_dependent(sentence, tok_id):
    for tok in sentence:
        if tok["deprel"] == "cop" and tok["head"] == tok_id:
            return True

    return False


# number of clauses in sentence function
def clauses_in_sent(sentence):
    clauses_counter = 1
    for tok in sentence:
        if tok["deprel"] in ["csubj", "ccomp", "xcomp", "advcl", "acl", "conj", "parataxis"] and \
                (tok["upos"] == "VERB" or has_cop_dependent(sentence, tok["id"])):
            clauses_counter += 1

    return clauses_counter


# number of T-units in sentence function
def t_units_in_sent(sentence):
    t_unit_counter = 1
    for tok in sentence:
        if tok["deprel"] in ["conj", "parataxis"] and \
                (tok["upos"] == "VERB" or has_cop_dependent(sentence, tok["id"])):
            t_unit_counter += 1

    return t_unit_counter


#####
# Measures from Terčon 2004 end here
#####