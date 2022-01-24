import json
import os
import shutil
from pkg_resources import resource_filename

def search_dict_list_by_key(dict_list, key, value):
    inx = 0
    res = []
    for i in range(len(dict_list)):
        if dict_list[i][key] in value:
            res.append(i)
    return res

def gen(classdic1, classdic2, map=None, path_name=None)->dict:
    S_label_dict_list = []
    F_label_dict_list = []
    word_dict_list = []
    for k,v in classdic1.items():
        for i in v:
            word_dict_list.append({"name":i, "value":1, "itemStyle":{"color":"#ef5a78"}})
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
    if map!=None:
        for i in word_dict_list:
            i["name"] = map[i["name"]]
    result = {"data": S_label_dict_list}
    if path_name:
        with open(path_name, "w") as jsonf:
            json_string = json.dumps(result, indent=4, sort_keys=True)
            jsonf.write(json_string)
    return result

def create_web(path_name, json_dic):
    os.mkdir(path_name)
    rf = resource_filename(__name__, "template")
    shutil.copy(os.path.join(rf,"echarts.js"), os.path.join(path_name, "echarts.js"))
    shutil.copy(os.path.join(rf,"test.html"), os.path.join(path_name, "test.html"))
    
    json_string = json.dumps(json_dic, indent=4, sort_keys=True).replace("\n","\\\n")

    with open(os.path.join(rf,"templatejs.txt"), "r") as tem:
        tem_string = tem.read()

    with open(os.path.join(path_name, "test.js"), "w") as js:
        js.write("var text='%s'\n\n%s"%(json_string, tem_string))

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
        for i in range(length):
            _color = [base_rgb_color[0], base_rgb_color[1]+grediant*(i+1), base_rgb_color[2]+grediant*(i+1)]
            for j in range(3):
                if _color[j]>255:
                    _color[j]=255
            _change_color(json_dic["children"][i], rgb_to_hex(tuple(_color)), grediant)

def grediant_color(json_dic, base_hex_color_list, grediant):
    data = json_dic["data"]
    assert len(base_hex_color_list)==len(data)
    for i,j in enumerate(data):
        _change_color(j, base_hex_color_list[i], grediant)