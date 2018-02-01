#!/usr/bin/python3

import sys
import requests
import io
import http.client
import base64
import json
import glob, os
from os.path import basename
from PIL import Image, ImageDraw, ExifTags
import scipy.misc
import numpy as np
from pprint import pprint
import time

if(len(sys.argv) != 2):
    print("Please provide enough arguments...\n")
    print("<file_name> <gallery_name>")
    exit(0)

print("\nGallery_name : ", sys.argv[1], "\n")

dir_path = "/home/Kairos/Kairos_Benchmark/Kairos_Demo/ms/"
json_path = "/home/Kairos/Kairos_Benchmark/Kairos_Demo/Recognization/json_files/"
rotate_path = "/home/Kairos/Kairos_Benchmark/Demo/rotate/"
Confidance_60_Path = "/home/Kairos/Kairos_Benchmark/Kairos_Demo/Recognization/Confidance_60_Path/"
Confidance_65_Path = "/home/Kairos/Kairos_Benchmark/Kairos_Demo/Recognization/Confidance_65_Path/"

detected_face = 0
recognized_faces = 0

Gallary_Name = ""
Subject_Id = ""

os.chdir(dir_path)

img = 0

def rotate_Image(fileName):
        try:
                os.chdir(rotate_path)
                image=Image.open(dir_path+fileName)
                for orientation in ExifTags.TAGS.keys():
                        if ExifTags.TAGS[orientation]=='Orientation':
                                break
                exif=dict(image._getexif().items())
                if exif[orientation] == 3:
                        image=image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                        image=image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                        image=image.rotate(90, expand=True)
                image.save(rotate_path+fileName)
                image.close()
                return(fileName)
        except Exception:
                pass

def file_Exist_Or_Not(directory):
        if not os.path.exists(directory):
                os.makedirs(directory)
                

def saveConfidanceInFile(Dir_path, fileName, confidance):
        with open(Dir_path+"/Confidance.txt", 'a') as f:
                f.write(fileName+" ==> ")
                f.write(str(confidance))
                f.write("\n")
                
                
def draw_rectangle(d, left, top, right, bottom, color, widthsize=4):
	d.line(((left, top), (right,top)), fill=color, width=widthsize)
	d.line(((left, top), (left,bottom)), fill=color, width=widthsize)
	d.line(((left, bottom), (right,bottom)), fill=color, width=widthsize)
	d.line(((right,top),(right,bottom)), fill=color, width=widthsize)

def build_payload(file):    
    if file is not None:
        image = extract_base64_contents(file)
    else:
        image = url
        
    values_enrol = {
       'image': image,
       'gallery_name': sys.argv[1],
    }

    return dict(values_enrol)

def extract_base64_contents(file):
    with open(file, 'rb') as fp:
        image = base64.b64encode(fp.read()).decode('ascii')
    return image

for file1 in glob.glob("*.jpg"):

    file = rotate_Image(file1)
    #img_path = file

    img = img + 1
    print("====== ",img," ======")
    print(file)

    tmp = 0
    cnt = 1
    is_Face_Rec = False

    #files = {'image': (img_path, open(dir_path + img_path, 'rb'), 'image/jpg', {'Expires': '0'})}

    headers = {
        'app_id': "xxxxxx",
        'app_key': "xxxxxxxxxxxxxxxxxxxxxxx",
    }

    payload = build_payload(file)
    
    try:
        res = requests.post('https://api.kairos.com/recognize', headers=headers, json=payload)
        #print(res.content)

        img1 = os.path.splitext(file)[0]
        #print(img1)

        file_Exist_Or_Not(json_path)
        
        dataJson = res.json()
        with open(json_path + img1+".json", 'w') as f:
                json.dump(dataJson, f)
        
        data = json.load(open(json_path+'/'+img1+'.json'))
            
        try:
            while(cnt != tmp):
                tmp1 = data["images"][cnt-1]["transaction"]["face_id"]
                cnt = cnt + 1
        except IndexError:
            tmp = cnt
            print("Detected Faces : ", tmp - 1)
            detected_face = detected_face + cnt - 1
            pass
                       
        picture_of_me = scipy.misc.imread(file)
        pil_image1 = Image.fromarray(picture_of_me)
        try:
            for i in range(0, tmp):
                X0 = data["images"][i]["transaction"]["topLeftX"]
                Y0 = data["images"][i]["transaction"]["topLeftY"]
                X1 = data["images"][i]["transaction"]["height"] + data["images"][i]["transaction"]["topLeftX"]
                Y1 = data["images"][i]["transaction"]["width"] + data["images"][i]["transaction"]["topLeftY"]
               
                d = ImageDraw.Draw(pil_image1,'RGBA')
                draw_rectangle(d, X0, Y0, X1, Y1, color="red", widthsize=5)
                face_rec = data["images"][i]["transaction"]["status"]
                #print(face_rec)
                if(face_rec == "success"):
                    print(face_rec)
                    print("Face Matched...")
                    Gallary_Name = data["images"][i]["transaction"]["gallery_name"]
                    Subject_Id = data["images"][i]["transaction"]["subject_id"]
                    print("Gallary Name : ",Gallary_Name)
                    print("Subject_Id :",Subject_Id)
                    draw_rectangle(d, X0, Y0, X1, Y1, color="black", widthsize=5)
                    recognized_faces = recognized_faces + 1
                    con = data["images"][i]["transaction"]["confidence"]
                    print(con)

                    file_Exist_Or_Not(Confidance_60_Path+Subject_Id)
                    file_Exist_Or_Not(Confidance_65_Path+Subject_Id)

                    if(con >= 0.65):
                            pil_image1.save(Confidance_65_Path+Subject_Id+"/"+file)
                            saveConfidanceInFile(Confidance_65_Path+Subject_Id+"/",file, con)
                    
                    pil_image1.save(Confidance_60_Path+Subject_Id+"/"+file)
                    saveConfidanceInFile(Confidance_60_Path+Subject_Id+"/",file, con)

                    draw_rectangle(d, X0, Y0, X1, Y1, color="green", widthsize=6)
                        
        except IndexError:
            pass

        time.sleep(1)
    except Exception as e:
        print(e)
        pass

print("Total images : ", img)
print("Total Detected faces : ", detected_face)
print("Total Recognized faces : ", recognized_faces)
