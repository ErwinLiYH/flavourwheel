from gensim import models as glove_model
from matplotlib import pyplot as plt
from numpy.core.numeric import outer
from . import k_cluster
from . import filters
import requests
import json
import numpy as np
import re
import os
import math

class GloVe_manager:
    def __init__(self, path):
        print("loading model please wait, it maight take few minutes.....")
        self.model = glove_model.KeyedVectors.load_word2vec_format(path, binary=False, no_header=True)
        print("init model %s successfully"%path)

def stanza_extracter(commands, nlp, POS=["NN", "JJ"]):
    POS_dtl = {i:[] for i in POS}
    for index, command in enumerate(commands):
        try:
            #print(command)
            doc = nlp(re.sub("-"," ",command.lower()))
            for i in POS:
                POS_dtl[i].append([word.lemma for sent in doc.sentences for word in sent.words if word.xpos==i])
            print("\rindex: %06d/%d"%(index+1,len(commands)),end="")
        except Exception as e:
            print("")
            print(command)
            print("")
            print(e)
    return POS_dtl
# POS_dtl : {"POS1": doc_token_list, "POS2": doc_token_list, ...}
# doc_token_list : [[token1, token2...] , [token1, token2] , ...]
#                      doc1                  doc2        ...
# log_list : [token1, token2, ...]
# doc_log_list : [log_list1, log_list2, ...]

def plot_POS_history(POS_dtl):
    length = len(POS_dtl)
    num_of_rows = math.ceil(length/2)
    num_of_columns = 2
    plt.figure(figsize=(num_of_columns*5 ,num_of_rows*2))
    index = 1
    counts = {}
    for k,v in POS_dtl.items():
        temp_set = set()
        counts[k] = []
        num_of_reviews = len(v)
        for i in v:
           temp_set.update(i)
           counts[k].append(len(temp_set))
    X = range(num_of_reviews)
    for k,v in counts.items():
        plt.subplot(num_of_rows, num_of_columns, index)
        plt.plot(X, v)
        index+=1
    plt.show()

def conclude(doc_token_list):
    count = {}
    for i in doc_token_list:
        for w in i:
            if w in count:
                count[w]+=1
            else:
                count[w] = 1
    return count

def merge_dtl(doc_token_list1, doc_token_list2):
    if len(doc_token_list1) != len(doc_token_list2):
        raise Exception("length of two doc_token_list must be same")
    doc_token_list = []
    for i in range(len(doc_token_list1)):
        doc_token_list.append(doc_token_list1[i]+doc_token_list2[i])
    return doc_token_list

def wordnet_filter(doc_token_list, disable_log = False):
    doc_log_list = []
    for i in range(len(doc_token_list)):
        log_list = []
        doc_token_list[i] = [j for j in doc_token_list[i] if filters.wordnet_boolean(j, log_list, disable_log=disable_log)]
        doc_log_list.append(log_list)
    return doc_log_list

def wordnet_adj2noun(doc_token_list, disable_log = False):
    doc_log_list = []
    for i in range(len(doc_token_list)):
        log_list = []
        doc_token_list[i] = filters.adj2noun(doc_token_list[i], log_list, disable_log=disable_log)
        doc_log_list.append(log_list)
    return doc_log_list

def MCG_filter(doc_token_list, num = 10, cache_path = "./MCG", disable_log = False):
    # try:
    #     os.mkdir(cache_path)
    # except:
    #     pass
    doc_log_list = []
    for i in range(len(doc_token_list)):
        log_list = []
        doc_token_list[i] = [j for j in doc_token_list[i] if filters.MCG_boolean(j, num=num, cache_path=cache_path, log_list=log_list, disable_log=disable_log)]
        doc_log_list.append(log_list)
    return doc_log_list

def frequency_filter(count, threshold):
    log_list = []
    remain = []
    for k,v in count.items():
        if v >= threshold:
            remain.append(k)
        else:
            log_list.append(k)
    return remain, log_list

def manual_filter(token_list, black_list = filters.defult_black_list):
    return [i for i in token_list if i not in black_list]

def to_GloVe_vector(token_list, model):
    vectors = []
    try:
        for i in range(len(token_list)):
            vectors.append(model.get_vector(token_list[i]))
    except:
        print("Error happend in %d"%i)
    vectors = np.stack(vectors)
    return vectors
        
def __gen_concept_matrix(token_list, num, cache_path = "./MCG"):
    classes = []
    info = []
    vectors = []
    for ind,i in enumerate(token_list):
        temp_dict = filters.get_concept_prob(i, num, cache_path = cache_path)
        classes += temp_dict.keys()
        classes = list(set(classes))
        info.append(temp_dict)
        print("\r%d/%d"%(ind+1,len(token_list)),end="")

    for i in classes:
        boolean_list = [filters.wordnet_boolean(i, disable_log=True) for i in i.split(" ")]
        if (True not in boolean_list):
            classes.remove(i)

    for i in info:
        temp_vect = [0 for i in range(len(classes))]
        for k,v in i.items():
            if k in classes:
                temp_vect[classes.index(k)] = v
        vectors.append(temp_vect)
    vectors = np.stack(vectors)
    return classes, vectors

def to_mix_vector(token_list, num_of_concept, GloVe_vectors, cache_path = "./MCG"):
    c, concept_matrix = __gen_concept_matrix(token_list, num_of_concept, cache_path = cache_path)
    vectors = np.hstack((GloVe_vectors, concept_matrix))
    print("\ngross concepts: %d"%len(c))
    return vectors

def cluster(linkage, outer_distence_threshold, inner_distence_threshold):
    if outer_distence_threshold >= inner_distence_threshold:
        raise Exception("outer_distence_threshold must small than inner_distence_threshold")
    root, Node_list = k_cluster.to_tree(linkage)
    k_cluster.compress_tree(Node_list, outer_distence_threshold)
    outer_relation = k_cluster.gen_classes(Node_list,outer_distence_threshold)
    k_cluster.clean_tree(Node_list,outer_distence_threshold)
    k_cluster.compress_tree(Node_list, inner_distence_threshold)
    inner_relation = k_cluster.gen_classes(Node_list, inner_distence_threshold)  
    return outer_relation, inner_relation