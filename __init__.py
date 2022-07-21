from matplotlib import pyplot as plt
from . import filters
from tqdm import tqdm
import numpy as np
# import re
import math
from . import conceptualize

def stanza_extracter(commants, nlp, POS=["NN", "JJ"]):
    POS_dtl = {i:[] for i in POS}
    for command in tqdm(commants):
        try:
            #print(command)
            # doc = nlp(re.sub("-"," ",command.lower()))
            doc = nlp(command)
            for i in POS:
                POS_dtl[i].append([word.lemma for sent in doc.sentences for word in sent.words if word.xpos==i])
            # print("\rindex: %06d/%d"%(index+1,len(commands)),end="")
        except Exception as e:
            print("")
            print(command)
            print("")
            print(e)
    return POS_dtl

def spacy_extracter(commants, nlp, POS=["NN", "JJ"]):
    POS_dtl = {i:[] for i in POS}
    for command in tqdm(commants):
        try:
            #print(command)
            # doc = nlp(re.sub("-"," ",command.lower()))
            doc = nlp(command)
            for i in POS:
                POS_dtl[i].append([w.lemma_ for w in doc if w.tag_==i])
            # print("\rindex: %06d/%d"%(index+1,len(commands)),end="")
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

def conclude(doc_token_list, verbose=False):
    count = {}
    for i in doc_token_list:
        for w in i:
            if w in count:
                count[w]+=1
            else:
                count[w] = 1
    if verbose:
        print("%d words totally"% len(count))
    return count

def merge_dtl(doc_token_list1, doc_token_list2):
    if len(doc_token_list1) != len(doc_token_list2):
        raise Exception("length of two doc_token_list must be same")
    doc_token_list = []
    for i in range(len(doc_token_list1)):
        doc_token_list.append(doc_token_list1[i]+doc_token_list2[i])
    return doc_token_list

def wordnet_filter(doc_token_list, num=3, disable_log = False):
    doc_log_list = []
    for i in range(len(doc_token_list)):
        log_list = []
        doc_token_list[i] = [j for j in doc_token_list[i] if filters.wordnet_boolean(j, log_list=log_list, disable_log=disable_log)]
        doc_log_list.append(log_list)
    return doc_log_list

def wordnet_adj2noun(doc_token_list, disable_log = False):
    doc_log_list = []
    for i in range(len(doc_token_list)):
        log_list = []
        doc_token_list[i] = filters.adj2noun(doc_token_list[i], log_list, disable_log=disable_log)
        doc_log_list.append(log_list)
    return doc_log_list

def MCG_filter(doc_token_list, num = 5, max_deepth=3, cache_path = "./MCG", concept_engin=None, method="network", disable_log = False):
    # try:
    #     os.mkdir(cache_path)
    # except:
    #     pass
    doc_log_list = []
    for i in tqdm(range(len(doc_token_list))):
        log_list = []
        if method=="network":
            doc_token_list[i] = [j for j in doc_token_list[i] if filters.MCG_boolean(j, num=num, max_deepth=max_deepth, cache_path=cache_path, log_list=log_list, disable_log=disable_log)]
        elif method=="local":
            doc_token_list[i] = [j for j in doc_token_list[i] if filters.MCG_boolean(j, num=num, max_deepth=max_deepth, cache_path=cache_path, concept_engin=concept_engin, method="local", log_list=log_list, disable_log=disable_log)]
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

def fast_filter(comments, conf):
    pass