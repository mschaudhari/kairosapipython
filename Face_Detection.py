#!/usr/bin/python3

import json
import requests
import io
import http.client
import base64
import glob, os
from os.path import basename
from PIL import Image, ImageDraw
import scipy.misc
import numpy as np
from pprint import pprint

dir_path = "/home/msc/Kairos/Photos/" 
json_path = "/home/msc/Kairos/kairos_jason/"
os.chdir(dir_path)

detected_face = 0
img = 0
def draw_rectangle(d, left, top, right, bottom, color, widthsize=4):
	d.line(((left, top), (right,top)), fill=color, width=widthsize)
	d.line(((left, top), (left,bottom)), fill=color, width=widthsize)
	d.line(((left, bottom), (right,bottom)), fill=color, width=widthsize)
	d.line(((right,top),(right,bottom)), fill=color, width=widthsize)

for file in glob.glob("*.jpg"):
    img_path = file

    img = img + 1
    print("====== ",img," ======")
    print(img_path)

    tmp = 0
    cnt = 1
    try:
            files = {'image': (img_path, open(dir_path + img_path, 'rb'), 'image/jpg', {'Expires': '0'})}

            headers = {
                'app_id': "xxxxxx",
                'app_key': "xxxxxxxxxxxxxx",
            }

            res = requests.post('https://api.kairos.com/detect', headers=headers, files=files)
            #print(res.content)
            
            dataJson = res.json()
            with open( json_path + "data.json", 'w') as f:
                    json.dump(dataJson, f)

            data = json.load(open(json_path+'/data.json'))
            #print(data)

            #print(data["images"])
            
            try:
                while(cnt != tmp):
                      tmp1 = data["images"][0]["faces"][cnt-1]["face_id"]
                      cnt = cnt + 1
            except IndexError:
                    tmp = cnt
                    detected_face = detected_face + cnt - 1
                    pass

            print("Total faces : ", cnt - 1)

                       
            picture_of_me = scipy.misc.imread(img_path)
            pil_image1 = Image.fromarray(picture_of_me)
            #new_p = pil_image1.convert('RGB')
            try:
                for i in range(0, tmp):
                        X0 = data["images"][0]["faces"][i]["topLeftX"]
                        Y0 = data["images"][0]["faces"][i]["topLeftY"]
                        X1 = data["images"][0]["faces"][i]["height"]+ data["images"][0]["faces"][i]["topLeftX"]
                        Y1 = data["images"][0]["faces"][i]["width"] + data["images"][0]["faces"][i]["topLeftY"]
                        #left, top, right, bottom
                        d = ImageDraw.Draw(pil_image1,'RGBA')
                        draw_rectangle(d, X0, Y0, X1, Y1, color="red", widthsize=5)
                        
        except IndexError:
                pass

        pil_image1.save("/home/msc/Kairos/Udagam_Recognization/"+file);
            
    except Exception as e:
        pass

print("Total images : ", img)
print("Total Detected faces : ", detected_face)
