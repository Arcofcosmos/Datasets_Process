'''
Author: TuZhou
Version: 1.0
Date: 2021-08-21 19:53:22
LastEditTime: 2021-08-29 18:06:07
LastEditors: TuZhou
Description: 划分数据集，将xml文件中的标注信息提取出与图片路径保存到新的txt文件中
FilePath: \My_Yolo\datasets\process_dataset.py
'''

from pathlib import Path
import yaml
import xml.etree.ElementTree as ET
from os import getcwd

import os
import random 
random.seed()

#自定义数据集配置文件的路径
yaml_path = './cfg/dataset.yaml'
#----------------------------------------------------------------------#
#   想要增加测试集修改trainval_percent
#   train_percent不需要修改
#----------------------------------------------------------------------#
trainval_percent = 0                  #所有数据集中训练集+验证集的比例
train_percent = 1                       #训练集+验证集中训练集的比例（可不管）默认1即可


'''
Author: TuZhou
Description: 读取数据集配置文件
param {*} yaml_path
return {*}返回配置文件中信息字典
'''
def read_dataset_yaml(yaml_path = './cfg/dataset.yaml'):
    yaml_file = Path(yaml_path)
    with open(yaml_file, encoding='utf-8') as f:
        yaml_dict = yaml.safe_load(f)
        
    return yaml_dict


'''
Author: TuZhou
Description: 从数据集中划分训练集，验证集，测试集，txt文件保存在ImageSets的Main文件夹中
param {*} xmlfilepath 数据集xml标注文件保存路径
param {*} saveSplitePath 数据集划分txt文件保存路径
return {*}
'''
def splite_dataset(xmlfilepath, saveSplitePath):

    #读取所有xml文件，存入列表中
    temp_xml = os.listdir(xmlfilepath)
    total_xml = []
    for xml in temp_xml:
        if xml.endswith(".xml"):
            total_xml.append(xml)

    #图片总数
    num = len(total_xml)  
    list = range(num)  
    numbers_tv = int(num * trainval_percent)            #获取训练和验证集数量
    numbers_train = int(numbers_tv * train_percent)  
    random.seed()
    trainval = random.sample(list, numbers_tv)          #从list中选取生成训练验证集的随机列表  
    random.seed()
    train = random.sample(trainval, numbers_train)                 #从训练验证集中选取生成训练集的随机列表


    print("train and val size: ", numbers_tv)
    print("train size: ", numbers_train)
    print("test size: ", num - numbers_tv)
    ftrainval = open(os.path.join(saveSplitePath,'trainval.txt'), 'w')  
    ftest = open(os.path.join(saveSplitePath,'test.txt'), 'w')  
    ftrain = open(os.path.join(saveSplitePath,'train.txt'), 'w')  
    fval = open(os.path.join(saveSplitePath,'val.txt'), 'w')  
    
    for i in list:  
        name=total_xml[i][:-4]+'\n'  
        if i in trainval:  
            ftrainval.write(name)  
            if i in train:  
                ftrain.write(name)  
            else:  
                fval.write(name)  
        else:  
            ftest.write(name)  
    
    ftrainval.close()  
    ftrain.close()  
    fval.close()  
    ftest .close()
    

def convert_annotation(xmlfilepath, image_id, list_file, classes):
    #in_file = open('VOCdevkit/VOC%s/Annotations/%s.xml'%(year, image_id), encoding='utf-8')
    in_file = open(xmlfilepath + '%s.xml'%(image_id), encoding='utf-8')
    tree=ET.parse(in_file)
    root = tree.getroot()

    for obj in root.iter('object'):
        difficult = 0 
        if obj.find('difficult')!=None:
            difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult)==1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (int(float(xmlbox.find('xmin').text)), int(float(xmlbox.find('ymin').text)), int(float(xmlbox.find('xmax').text)), int(float(xmlbox.find('ymax').text)))
        list_file.write(" " + ",".join([str(a) for a in b]) + ',' + str(cls_id))
        #print(" " + ",".join([str(a) for a in b]) + ',' + str(cls_id))


def save_dataset_info(yaml_dict):
    wd = getcwd()
    sets = yaml_dict['sets']
    saveSplitePath = yaml_dict['saveSplitePath']
    xmlfilepath = yaml_dict['xmlfilepath']
    processedPath = yaml_dict['DatasetPath']
    ImagesDir = yaml_dict['ImagesDir']
    classes = yaml_dict['classes']
    image_format = yaml_dict['image_format']
    for image_set in sets:
        # image_ids = open('VOCdevkit/VOC%s/ImageSets/Main/%s.txt'%(year, image_set), encoding='utf-8').read().strip().split()
        # list_file = open('%s_%s.txt'%(year, image_set), 'w', encoding='utf-8')
        #读取划分后的图片名文件
        image_ids = open(saveSplitePath + '%s.txt'%(image_set), encoding='utf-8').read().strip().split()
        #创建要保存路径和标注的txt文件
        list_file = open(processedPath + '%s.txt'%(image_set), 'w', encoding='utf-8')

        for image_id in image_ids:
            #list_file.write('%s/VOCdevkit/VOC%s/JPEGImages/%s.jpg'%(wd, year, image_id))
            list_file.write(wd + ImagesDir +  image_id + image_format)
            convert_annotation(xmlfilepath, image_id, list_file, classes)
            list_file.write('\n')
        list_file.close()
        

if __name__ == '__main__':
    yaml_dict = read_dataset_yaml(yaml_path)
    #划分数据集
    xmlfilepath, saveSplitePath = yaml_dict['xmlfilepath'], yaml_dict['saveSplitePath']
    splite_dataset(xmlfilepath, saveSplitePath)
    #保存数据集信息，即图片路径以及标注信息
    save_dataset_info(yaml_dict)
    