'''
Author: TuZhou
Version: 1.0
Date: 2021-09-11 16:50:47
LastEditTime: 2021-09-12 09:42:32
LastEditors: TuZhou
Description: 图片文件名 x1 y1 x2 y2 label…
FilePath: \python_test\txt_to_coco.py
'''
import json
import cv2
import path
import os


#第一个coco json类型
bnd_id_start = 1

#NOTE：你的分类
class_map = {"tamper":0}
#你的图片id，可自定义
my_image_id = 20210000000

times = 0

json_dict = {
    "images"     : [],
    "type"       : "instances",
    "annotations": [],
    "categories" : []
}

'''
Author: TuZhou
Description: 
param {*} L1：你的标注列表信息，注意只包含x1,y1,x2,y2,label,如[234,43,345,213,'person',34,54,23,34,'dog']
param {*} numbers：你要切分的长度，x1,y1,x2,y2,label长度为5
return {*}返回包含所有目标信息的二维列表
'''
def get_list_value(L1, numbers):
    obj_list = []
    for i in range(0, len(L1), numbers):
        l2 = L1[i: i + numbers]
        obj_list.append(l2)
    return obj_list


# NOTE：这里是你的txt文件的读取
with open(r'E:\user\baidu_pan\CASIA_object_detection\annotations.txt','r') as f:
    data = f.readlines()

bnd_id = bnd_id_start

#NOTE：这是你的图片格式，如果支持多种图片文件
images_format = ['.jpg', '.tif']


for d in data:
    content = d.strip().split(" ")
    print(content)
    filename = content[0]     #这里可能修改，txt文件每一行第一个属性是图片路径，通过split()函数把图像名分离出来就行
    for image_format in images_format:
        #NOTE：你的图片文件路径要改
        image_path = 'E:\\user\\baidu_pan\\CASIA_object_detection\\CAISA_Train_Images\\' + content[0] + image_format
        if os.path.exists(image_path):
            break
    img = cv2.imread(image_path)
    print(image_path)
    try:
        height,width = img.shape[0],img.shape[1]
        image_id = my_image_id
        my_image_id += 1
    except:
        times +=1
        print('file is error')

# type 已经填充

#定义image 填充到images里面
    image = {
        'file_name' : filename,  #文件名
        'height'    : height,    #图片的高
        'width'     : width,     #图片的宽
        'id'        : image_id   #图片的id，和图片名对应的
    }
    json_dict['images'].append(image)

    #print(content[5])
    # start_index = 1
    # if start_index != len(content) - 1:
    obj_lists = get_list_value(content[1:],5)
    for obj_list in obj_lists:
        #print(c)
        #xmin,ymin,xmax,ymax,label = c.strip().split(" ")
        xmin = int(obj_list[0])
        ymin = int(obj_list[1])
        xmax = int(obj_list[2])
        ymax = int(obj_list[3])
        o_width = abs(int(xmax) - int(xmin))
        o_height = abs(int(ymax) - int(ymin))

        area = o_width * o_height
        category_id = class_map[obj_list[4]]

        # #定义annotationhb
        annotation = {
            'area'          : area,  #
            'iscrowd'       : 0,
            'image_id'      : image_id,  #图片的id
            'bbox'          :[xmin, ymin, o_width,o_height],
            'category_id'   : int(category_id), #类别的id 通过这个id去查找category里面的name
            'id'            : bnd_id,  #唯一id ,可以理解为一个框一个Id
            'ignore'        : 0,
            'segmentation'  : []
        }
        print(category_id)

        json_dict['annotations'].append(annotation)

        bnd_id += 1
    #
#定义categories

#你得类的名字(cid,cate)对应
classes = ['tamper']

for i in range(len(classes)):

    cate = classes[i]
    cid = i
    category = {
        'supercategory' : 'none',
        'id'            : cid,  #类别的id ,一个索引，主键作用，和别的字段之间的桥梁
        'name'          : cate  #类别的名字比如房子，船，汽车
    }

    json_dict['categories'].append(category)



json_fp = open("train.json",'w')
json_str = json.dumps(json_dict)
json_fp.write(json_str)
json_fp.close()
