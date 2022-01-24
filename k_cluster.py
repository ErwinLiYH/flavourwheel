import numpy as np
# import pickle
import matplotlib.pyplot as plt


# def load_result(path_name):
#     with open(path_name, "rb") as f:
#         return pickle.load(f)

class Node:
    def __init__(self, id, dist, parent, children_list):
        self.id = id
        self.dist = dist
        self.parent = parent
        self.children_list = children_list

def gen_classes(Node_list, dist_tol)->dict:
    res = {}
    for i in Node_list:
        if i.children_list == []:
            if i.parent.id in res:
                if i.parent.dist<dist_tol:
                    res[i.parent.id].append(i.id)
                else:
                    res[i.id].append(i.id)
            else:
                if i.parent.dist<dist_tol:
                    res[i.parent.id] = [i.id]
                else:
                    res[i.id] = [i.id]
    return res

def get_sub_node(Node):
    res = []
    if Node.children_list == []:
        return [Node]
    for i in Node.children_list:
        res += get_sub_node(i)
    return res

def merge_node(Node):
    node_list = get_sub_node(Node)
    for i in node_list:
        i.parent = Node
    Node.children_list = node_list

def compress_tree(Node_list, dist_tol):
    for i in Node_list:
        if i.children_list == []:
            pass
        else:
            if i.dist<dist_tol:
                merge_node(i)

def to_tree(linkage):
    # generate multi_tree from linkage matrix
    n = linkage.shape[0] + 1
    Node_list = [Node(i, 0, None, []) for i in range(n)]
    for i in range(n-1):
        nd = Node(n+i, linkage[i][2], None, [Node_list[int(linkage[i][0])], Node_list[int(linkage[i][1])]])
        Node_list[int(linkage[i][0])].parent = nd
        Node_list[int(linkage[i][1])].parent = nd
        Node_list.append(nd)
    return nd, Node_list

def clean_tree(Node_list, dist_tol):
    remove_list = []
    for i in Node_list:
        if i.parent == None:
            pass
        else:
            if i.parent.dist < dist_tol and i.children_list == []:
                i.parent.children_list.remove(i)
                remove_list.append(i)
    for i in remove_list:
        Node_list.remove(i)
    remove_list = []
    for i in Node_list:
        for j in i.children_list:
            if j not in Node_list:
                remove_list.append(i)
                break
    for i in remove_list:
        Node_list.remove(i)

def PCA_elbow_plot(linkage, dist=None):
    dist_range = np.arange(np.amin(linkage, axis=0)[2], np.amax(linkage, axis=0)[2], step=0.01)
    class_num = []
    for i in dist_range:
        root, temp_list = to_tree(linkage)
        compress_tree(temp_list, i)
        class_num.append(len(gen_classes(temp_list, i)))
    plt.plot(dist_range, class_num)  
    if dist:
        plt.axvline(dist, color="red")



    

# if __name__ == "__main__":
#     all_w = load_result("all_words.list")
#     vecs = load_result("./matrixes/mix_version/mix_glove.840B.300d.ndarray")
#     mx = vecs
#     #mx = sch.linkage(data, method='average',metric="cosine")
#     myroot, Node_list = to_tree(mx)

#     # elbow_plot(mx)
#     first_dist = 0.47
#     second_dist = 0.65
#     compress_tree(Node_list, first_dist)
#     l1 = gen_classes(Node_list, first_dist)
#     print(first_dist)
#     clean_list(Node_list)
#     compress_tree(Node_list, second_dist)
#     l2 = gen_classes(Node_list, second_dist)
#     print(second_dist)
#     gen(l1,l2,map = all_w, for_js=False)
#     # print("xxx")
#     # plt.savefig("test.png")