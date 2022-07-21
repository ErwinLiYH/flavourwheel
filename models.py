from gensim import models as glove_model
import numpy as np
from tqdm import tqdm
from . import filters
from . import conceptualize

class GloVe:
    def __init__(self, FD, model_path):
        print("loading model please wait, it maight take few minutes.....")
        self.GloVe_model = glove_model.KeyedVectors.load_word2vec_format(model_path, binary=False, no_header=True)
        print("init model %s successfully"%model_path)
        self.FD = FD
    def to_vector(self):
        vectors = []
        try:
            for i in range(len(self.FD)):
                vectors.append(self.GloVe_model.get_vector(self.FD[i]))
        except:
            print("Error happend in %d"%i)
            raise Exception()
        vectors = np.stack(vectors)
        return vectors

class MCG:
    def __init__(self, FD, num, cache_path = "./MCG", engin_path=None, method = "network"):
        self.FD = FD
        self.num = num
        self.cache_path = cache_path
        self.method = method
        if self.method=="local":
            self.engin = conceptualize.ProbaseConcept(engin_path)
        elif self.method=="network":
            self.engin = None
    def __gen_concept_matrix(self):
        classes = []
        info = []
        vectors = []
        for i in tqdm(self.FD):
            temp_dict = filters.get_concept_prob(i, self.num, cache_path = self.cache_path, concept_engin = self.engin, method = self.method)
            classes += temp_dict.keys()
            classes = list(set(classes))
            info.append(temp_dict)
            # print("\r%d/%d"%(ind+1,len(token_list)),end="")

        remove_list = []
        for i in classes:
            boolean_list = [filters.wordnet_boolean(i, disable_log=True) for i in i.split(" ")]
            if (True not in boolean_list):
                # classes.remove(i)
                remove_list.append(i)
        for i in remove_list:
            classes.remove(i)

        classes.sort()

        for i in info:
            temp_vect = [0 for i in range(len(classes))]
            for k,v in i.items():
                if k in classes:
                    temp_vect[classes.index(k)] = v
            vectors.append(temp_vect)
        vectors = np.stack(vectors)
        return classes, vectors
    
    def to_vector(self, verbose=False):
        c, concept_matrix = self.__gen_concept_matrix()
        if verbose:
            return c, concept_matrix
        else:
            return concept_matrix


class mixed_model:
    def __init__(self, vec1, vec2, weight_part1=0.5, weight_part2=0.5):
        self.vec1 = vec1
        self.vec2 = vec2
        self.weight1 = weight_part1
        self.weight2 = weight_part2
        self.len_part1 = vec1.shape[1]
    
    def __cosine(self, x, y):
        res = 1 - (np.dot(x,y.T)/(np.linalg.norm(x)*np.linalg.norm(y)))
        return res

    def mixed_distance(self, vect1, vect2):
        len_part1 = self.len_part1
        weight_part1 = self.weight1
        weight_part2 = self.weight2
        a = np.array(vect1[0:len_part1])
        b = np.array(vect2[0:len_part1])
        c = np.array(vect1[len_part1:])
        d = np.array(vect2[len_part1:])
        dist1 = self.__cosine.__call__(a,b)
        dist2 = self.__cosine.__call__(c,d)
        return weight_part1*dist1+weight_part2*dist2

    def to_vectors(self):
        vectors = np.hstack((self.vec1, self.vec2))
        return vectors