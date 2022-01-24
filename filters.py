from nltk.corpus import wordnet as wn

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

def manual_filter(token, black_list):
    if token in black_list:
        return True
    else:
        return False

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