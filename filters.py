from termios import CINTR
from nltk.corpus import wordnet as wn
from Kkit import prj_control
import json
import requests
import os
from . import conceptualize as concept

requests.packages.urllib3.disable_warnings()

black_list1 = ["dessert","coffee", "latte", "americano", "java", "demitasse", "cappuccino","espresso", "milk"] # coffee related words
black_list2 = ["dinner","lunch","breakfast","water", "food", "delicacy"] # too comprehensive words
black_list3 = ["course", "frank", "cube", "brittle", "concentrate", "tongue", "mix", "mace", "board",
               "delicacy", "bay", "center", "round", "taste", "serving", "cut",
               "spine", "sticker", "fuzz", "peppercorn", "center", "centre", "side", "cup", "cupper",
               "gall", "green", "cream", "butter", "stone", "bit", "relish", "blossom", "bloom", "flower", "crisp", "chip",
               "juice", "tart", "tea", "syrup", "nut", "spice", "roast", "sour", "fruit", "sugar", "sweet", "cocoa", "cacao", "berry", "citrus", "herb"] # others

defult_black_list = black_list1+black_list2+black_list3

def wordnet_boolean(token, log_list=None, disable_log=False):
    lexname_list = [j.lexname() for j in wn.synsets(token,pos=wn.NOUN)]
    x = ("noun.food" in lexname_list or "noun.plant" in lexname_list)
    if x == True:
        return x
    else:
        if disable_log==False:
            log_list.append(token)
        return x

def get_concept_prob(word, num, cache_path = "./MCG", concept_engin = None, method = "network") -> dict:
    if method == "network":
        cache_list = []
        try:
            cache_list = os.listdir(cache_path)
        except:
            os.mkdir(cache_path)
        if "%s_%d"%(word,num) in cache_list:
            res = prj_control.load_result(os.path.join(cache_path, "%s_%d"%(word,num)))
            return res
        else:
            link = requests.get("https://concept.research.microsoft.com/api/Concept/ScoreByProb?instance=%s&topK=%d"%(word, num), verify=False)
            if link.status_code == 200:
                res = json.loads(link.text)
                prj_control.store_result(os.path.join(cache_path,"%s_%d"%(word,num)),res)
                return res
            else:
                raise Exception("code: %d"%link.status_code)
    if method == "local":
        res = {}
        concept_list = concept_engin.conceptualize(word, score_method="likelihood")[:num]
        total = 0
        for i in concept_list:
            total+=i[1]
        for i in concept_list:
            res[i[0]] = i[1]/total
        return res


def __check(token, A_list):
    x = [i.split(" ") for i in A_list]
    y = []
    for i in x:
        y.append(i[-1])
    if token in y:
        return True
    else:
        return False

def MCG_boolean(token, num, max_deepth=3, cache_path="./MCG", concept_engin = None, method = "network", log_list=None, disable_log=False):
    tokens = [token]
    for i in range(max_deepth):
        temp_tokens=[]
        for j in tokens:
            try:
                prob_dic = get_concept_prob(j, num, cache_path, concept_engin = concept_engin, method = method)
            except:
                print(j)
                exit(0)
            if len(prob_dic)!=0:
                keys_list = list(prob_dic.keys())
                if True in [__check(i, keys_list) for i in ["plant", "food", "crop", "oil"]]:
                    return True
                temp_tokens+=list(keys_list)
        tokens = temp_tokens
    if disable_log==False:
        log_list.append(token)
    return False

def MCG_boolean_old(token, num, cache_path = "./MCG", log_list=None, disable_log=False):
    prob_dic = get_concept_prob(token, num, cache_path)
    boolean_list = []
    for k,v in prob_dic.items():
        boolean_list.append(True in [wordnet_boolean(k, disable_log=True) for k in k.split(" ")])
    x = (True in boolean_list)
    if x == True:
        return x
    else:
        if disable_log==False:
            log_list.append(token)
        return x

# def manual_filter(token, black_list):
#     if token in black_list:
#         return True
#     else:
#         return False

def adj2noun(adj_lemma_list, log_list=None, disable_log=False):
    noun_list = [] # [[], [], []]
    for i in adj_lemma_list:
        synsets = []
        nouns = []
        for j in [x.derivationally_related_forms() for x in wn.lemmas(i) if x.synset().pos() in ["a","s"]]:
            for k in j:
                synsets.append(k.synset())
        for j in synsets:
            if j.pos() == "n":
                nouns+=(j.lemma_names())
        noun_list.append(nouns)
    # for i in range(len(noun_list)):
    #     noun_list[i] = [x.lower() for x in noun_list[i] if wordnet_filter(x.lower())]
    noun_list = [list(set(i)) for i in noun_list] # remove repetition
    result = [x.lower() for l in noun_list for x in l if len(x.split("_"))==1]
    # write a log to check the perfomance
    if disable_log==False:
        for i in range(len(adj_lemma_list)):
            log_list.append({adj_lemma_list[i]: noun_list[i]})
    return result