import json
import os
import shutil
from pkg_resources import resource_filename
import scipy.cluster.hierarchy as sch
from mlhCluster import twoL

def search_dict_list_by_key(dict_list, key, value):
    inx = 0
    res = []
    for i in range(len(dict_list)):
        if dict_list[i][key] in value:
            res.append(i)
    return res

# def gen(classdic1, classdic2, map=None, path_name=None, remove_duplicate=False, num_of_words=None)->dict:
def gen(classdic1, classdic2, FD_map=None, path_name=None)->dict:
    # if remove_duplicate and map!=None and num_of_words!=None:
    #     for k,v in classdic1.items():
    #         remove_id = []
    #         for i in range(len(v)):
    #             if i not in remove_id:
    #                 p = map[v[i]]
    #                 for j in range(i+1, len(v)):
    #                     if map[v[j]] == p:
    #                         remove_id.append(j)
    #         temp = [j for i,j in enumerate(v) if i not in remove_id]
    #         v.clear()
    #         for i in temp:
    #             v.append(i)
    #     for k,v in classdic2.items():
    #         remove_id = []
    #         for i in range(len(v)):
    #             if i not in remove_id and v[i]<(num_of_words-1):
    #                 p = map[v[i]]
    #                 for j in range(i+1, len(v)):
    #                     if map[v[j]] == p:
    #                         remove_id.append(j)
    #         temp = [j for i,j in enumerate(v) if i not in remove_id]
    #         v.clear()
    #         for i in temp:
    #             v.append(i)
    #     common_part = [val[0] for val in classdic1.items() if val in classdic2.items()]
    #     remove_id = []
    #     for i in range(len(common_part)):
    #         if i not in remove_id:
    #             p = map[common_part[i]]
    #             for j in range(i+1, len(common_part)):
    #                 if map[common_part[j]] == p:
    #                     remove_id.append(common_part[j])
    #     for i in remove_id:
    #         classdic1.pop(i)
    #         classdic2.pop(i)
    S_label_dict_list = []
    F_label_dict_list = []
    word_dict_list = []
    for k,v in classdic1.items():
        for i in v:
            word_dict_list.append({"name":i, "children":[], "value":1, "itemStyle":{"color":"#ef5a78"}})
    for k,v in classdic1.items():
        dic = {"name":k, "children":[], "itemStyle":{"color":"#ef5a78"}}
        inx = search_dict_list_by_key(word_dict_list, "name", [k])
        inx2 = search_dict_list_by_key(word_dict_list, "name", v)
        if len(inx) != 0:
            if word_dict_list[inx[0]]["name"] == k:
                dic=word_dict_list[inx[0]]
        else:
            for i in inx2:
                dic["children"].append(word_dict_list[i])
        F_label_dict_list.append(dic)
    for k,v in classdic2.items():
        dic = {"name":k, "children":[], "itemStyle":{"color":"#ef5a78"}}
        inx = search_dict_list_by_key(F_label_dict_list, "name", [k])
        inx2 = search_dict_list_by_key(F_label_dict_list, "name", v)
        if len(inx) != 0:
            if F_label_dict_list[inx[0]]["name"] == k:
                dic=F_label_dict_list[inx[0]]
        else:
            for i in inx2:
                dic["children"].append(F_label_dict_list[i])
        S_label_dict_list.append(dic)
    if FD_map!=None:
        for i in word_dict_list:
            i["name"] = FD_map[i["name"]]
    result = {"data": S_label_dict_list}
    if path_name:
        with open(path_name, "w") as jsonf:
            json_string = json.dumps(result, indent=4, sort_keys=True)
            jsonf.write(json_string)
    return result

def create_web(path_name, json_dic):
    try:
        os.makedirs(path_name)
    except:
        switch = input("%s existed, delete it? (yes/no): "%path_name)
        if switch == "yes":
            shutil.rmtree(path_name)
            os.makedirs(path_name)
        else:
            print("create web failed")
            return
    rf = resource_filename(__name__, "data")
    shutil.copy(os.path.join(rf,"echarts.js"), os.path.join(path_name, "echarts.js"))
    shutil.copy(os.path.join(rf,"test.html"), os.path.join(path_name, "test.html"))
    
    json_string = json.dumps(json_dic, indent=4, sort_keys=True).replace("\n","\\\n")

    with open(os.path.join(rf,"template.js"), "r") as tem:
        tem_string = tem.read()

    with open(os.path.join(path_name, "test.js"), "w") as js:
        js.write("var text='%s'\n\n%s"%(json_string, tem_string))

def one_step_dtermine_distance(vecs, linkage_metric="cosine", linkage_method="average", start=0, end=1, step=0.001, figsize=(10,16), img_path=None, dpi=600):
    return twoL.one_step_determine_distance(vecs, linkage_metric, linkage_method, start, end, step, figsize, img_path, dpi)

def one_step_flavourwheel(vecs, FD_map, outer_distance, inner_distance, web_path, remove_duplicate=False, group_num=10, json_path=None):
    linkage_matrix = sch.linkage(vecs, method="average", metric="cosine")
    outer_relation,inner_relation = twoL.cluster(linkage=linkage_matrix, outer_distance_threshold=outer_distance, inner_distance_threshold=inner_distance)
    if remove_duplicate:
        twoL.remove_duplicate(outer_relation, inner_relation, vecs.shape[0], group_num)
    json_dict = gen(outer_relation, inner_relation, FD_map=FD_map, path_name=json_path)
    create_web(web_path, json_dict)

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

def _change_color(json_dic, base_hex_color, grediant):
    json_dic["itemStyle"]["color"] = base_hex_color
    if "children" in json_dic:
        length = len(json_dic["children"])
        base_rgb_color = hex_to_rgb(base_hex_color)
        if length != 0:
            base_grediant = grediant//length
            for i in range(length):
                _color = [base_rgb_color[0], base_rgb_color[1]+base_grediant*(i+1), base_rgb_color[2]+base_grediant*(i+1)]
                for j in range(3):
                    if _color[j]>255:
                        _color[j]=255
                _change_color(json_dic["children"][i], rgb_to_hex(tuple(_color)), grediant)

def grediant_color(json_dic, base_hex_color_list, grediant):
    data = json_dic["data"]
    assert len(base_hex_color_list)==len(data)
    for i,j in enumerate(data):
        _change_color(j, base_hex_color_list[i], grediant)

# inner layer is layer 1, outer layer is layer 3
def value_check(json_dic):
    for i in json_dic["data"]:
        if i["children"] == [] and "value" not in i:
            i["value"] = 1
        for j in i["children"]:
            if j["children"] == [] and "value" not in j:
                j["value"] = 1
            for k in j["children"]:
                if k["children"] == [] and "value" not in k:
                    k["value"] = 1
    for i in json_dic["data"]:
        if i["children"] != [] and "value" in i:
            i.pop("value")
        for j in i["children"]:
            if j["children"] != [] and "value" in j:
                j.pop("value")
            for k in j["children"]:
                if k["children"] != [] and "value" in k:
                    k.pop("value")


def add_cluster(json_dict, cluster_id, parent_id=None, parent_layer=0):
    flag = False
    if parent_layer not in [0,1,2]:
        raise Exception("The parent layer must be 0 to 2")
    if parent_layer == 0:
        json_dict["data"].append({"name":cluster_id, "children":[], "itemStyle":{"color":"#ef5a78"}})
    if parent_layer == 1:
        for i in json_dict["data"]:
            if i["name"] == parent_id:
                i["children"].append({"name":cluster_id, "children":[], "itemStyle":{"color":"#ef5a78"}})
                break
    if parent_layer == 2:
        for i in json_dict["data"]:
            for j in i["children"]:
                if j["name"] == parent_id:
                    j["children"].append({"name":cluster_id, "children":[], "itemStyle":{"color":"#ef5a78"}})
                    flag = True
                    break
            if flag:
                break
    value_check(json_dict)

def search_dic_by_name(dic_list, id):
    for i in dic_list:
        if i["name"] == id:
            return i

def substract_cluster(json_dict, cluster_id, layer):
    flag = False
    if layer not in [1,2,3]:
        raise Exception("The layer must be 1 to 3")
    if layer == 1:
        sub = search_dic_by_name(json_dict["data"], cluster_id)
        json_dict["data"].remove(sub)
    if layer == 2:
        for i in json_dict["data"]:
            sub = search_dic_by_name(i["children"], cluster_id)
            if sub != None:
                i["children"].remove(sub)
                break
    if layer == 3:
        for i in json_dict["data"]:
            for j in i["children"]:
                sub = search_dic_by_name(j["children"], cluster_id)
                if sub != None:
                    j["children"].remove(sub)
                    flag = True
                    break
            if flag:
                break
    value_check(json_dict)

def move_cluster(json_dict, id, layer, to_parent_id=None, to_parent_layer=0):
    if layer not in [1,2,3]:
        raise Exception("The layer must be 1 to 3")
    if to_parent_layer not in [0,1,2]:
        raise Exception("The parent to_parent_layer must be 0 to 2")
    substract_cluster(json_dict, id, layer)
    add_cluster(json_dict, id, parent_id=to_parent_id, parent_layer=to_parent_layer)

def compress_cluster(json_dict, id, layer):
    flag = False
    if layer not in [1,2]:
        raise Exception("The layer must be 1 to 2")
    if layer == 1:
        for i in json_dict["data"]:
            if i["name"] == id:
                for j in i["children"]:
                    json_dict["data"].append(j)
                substract_cluster(json_dict, id, 1)
                break
    if layer == 2:
        for i in json_dict["data"]:
            for j in i["children"]:
                if j["name"] == id:
                    for k in j["children"]:
                        add_cluster(json_dict, k["name"], i["name"], 1)
                    substract_cluster(json_dict, id, 2)
                    flag = True
                    break
            if flag:
                break

def replace_name(json_dict, id, layer, to_id):
    flag = False
    if layer not in [1,2,3]:
        raise Exception("The layer must be 1 to 3")
    if layer == 1:
        for i in json_dict["data"]:
            if i["name"] == id:
                i["name"] = to_id
                break
    if layer == 2:
        for i in json_dict["data"]:
            for j in i["children"]:
                if j["name"] == id:
                    j["name"] = to_id
                    flag = True
                    break
            if flag:
                break
    if layer == 3:
        for i in json_dict["data"]:
            for j in i["children"]:
                for k in j["children"]:
                    if k["name"] == id:
                        k["name"] = to_id
                        flag = True
                        break
                if flag:
                    break
            if flag:
                break

def find_name(a_cluster_list, name):
    for i, o in enumerate(a_cluster_list):
        if o["name"] == name:
            return i

def change_order(json_dict, order_list, id=None, layer=0):
    flag = False
    if layer==0:
        for i in range(len(json_dict["data"])):
            if json_dict["data"][i]["name"] != order_list[i]:
                index = find_name(json_dict["data"], order_list[i])
                json_dict["data"][index], json_dict["data"][i] = json_dict["data"][i], json_dict["data"][index]
    elif layer == 1:
        for i in json_dict["data"]:
            if i["name"] == id:
                for j in range(len(i["children"])):
                    if i["children"][j]["name"] != order_list[j]:
                        index = find_name(i["children"], order_list[j])
                        i["children"][index], i["children"][j] = i["children"][j], i["children"][index]
                break
    elif layer == 2:
        for i in json_dict["data"]:
            for j in i["children"]:
                if j["name"] == id:
                    for k in range(len(j["children"])):
                        if j ["children"][k]["name"] != order_list[k]:
                            index = find_name(j["children"], order_list[k])
                            j["children"][index], j["children"][k] = j["children"][k], j["children"][index]
                    flag = True
                if flag:
                    break
            if flag:
                break
    else:
        raise Exception("The layer must be 1 to 3")

def search_by_id(json_dict, id):
    for i in json_dict["data"]:
        if i["name"] == id:
            return i
        for j in i["children"]:
            if j["name"] == id:
                return j
            for k in j["children"]:
                if k["name"] == id:
                    return k
    print("warning: %s is not existed"%id)

def replace_color2(json_dict, id, to_color):
    x = search_by_id(json_dict=json_dict, id=id)
    x["itemStyle"]["color"] = to_color

def capitalize(i):
    i["name"] = i["name"].capitalize()

def traverse(json_dict, call_back = capitalize):
    for i in json_dict["data"]:
        call_back.__call__(i)
        for j in i["children"]:
            call_back.__call__(j)
            for k in j["children"]:
                call_back.__call__(k)