#!/usr/bin/python3
    
import requests
import io
import http.client
import base64
import json
import glob, os
from os.path import basename
import sys

if(len(sys.argv) != 4):
    print("Please provide enough arguments...\n")
    print("<file_name> <subject_id> <gallery_name> <Profile Pic's Path>\n")
    exit(0)

dir_path = os.path.dirname(sys.argv[3])
#print(dir_path)
os.chdir(dir_path)

def profile_pic_enroll(headers, payload):
    res = requests.post('https://api.kairos.com/enroll', headers=headers, json=payload)
    print("Successfully Profile Picture added.\nThank you.\n\n")
    #print(res.content)

def view_gallary(headers, payload):
    res = requests.post('https://api.kairos.com/gallery/view', headers=headers, json=payload)
    #print(res.content)
    return res

def view_subject_id(headers, payload):
    subject_Id = {
       'subject_id': sys.argv[1],
       'gallery_name': sys.argv[2],
    }
    try:
        subject_id_res = requests.post('https://api.kairos.com/gallery/view_subject', headers=headers, json=subject_Id)
        #print(res.content)
        sub_id_obj = json.loads(subject_id_res.content.decode('utf-8'))
        if((sub_id_obj['Errors'][0]['Message']) == "subject id was not found"):
            profile_pic_enroll(headers, payload)
            return 0
    except KeyError:
        pass

    return 1
    
def verify_profile_picture(file, headers, payload):
    res = requests.post('https://api.kairos.com/verify', headers=headers, json=payload)
    #print(res.content)
    return res

def build_payload(file):
    print("\nsubject_id : ", sys.argv[1])
    print("gallery_name : ", sys.argv[2], "\n")
    
    if file is not None:
        image = extract_base64_contents(file)
    else:
        image = url
        
    values_enrol = {
       'image': image,
       'subject_id': sys.argv[1],
       'gallery_name': sys.argv[2],
    }

    return dict(values_enrol)

def extract_base64_contents(file):
    with open(file, 'rb') as fp:
        image = base64.b64encode(fp.read()).decode('ascii')
    return image
    
def save_verify_confidance(varify_res):
    ret = 0
    json_obj_varify = json.loads(varify_res.content.decode('utf-8'))
    json_conf = json_obj_varify['images'][0]['transaction']['confidence']

    with open(dir_path + "/verify.txt", 'ab') as fp:
        if (os.stat(dir_path + "/verify.txt").st_size == 0):
            fp.write(str(json_conf).encode('utf-8'))
            fp.write(str("\n").encode('utf-8'))
    fp.close()
    
    con = read_json_file(dir_path+"/verify.txt")
        
    tmp = 0
    for x in con[:]:
        if(str(json_conf) == x):
            tmp = 1
            
    if(tmp == 0):
        with open(dir_path + "/verify.txt", 'ab') as fp1:
            fp1.write(str(json_conf).encode('utf-8'))
            fp1.write(str("\n").encode('utf-8'))
            ret = 1
        fp1.close()
        
    return ret

def read_json_file(jFile):
    data = []
    
    with open(jFile) as f:
        content = f.readlines()
        data = [x.strip() for x in content]
        return data

# Upload the profile Picture
file = sys.argv[3]

# Check authentication
headers = {
    'app_id': "xxxx",
    'app_key': "xxxxxxxxxxxxxxxxxxxxxxxxx",
}

payload = build_payload(file)

gallary = {
   'gallery_name': sys.argv[2],
}

try:
    gallary_res = view_gallary(headers, gallary)
    json_obj = json.loads(gallary_res.content.decode('utf-8'))
    
    if((json_obj['Errors'][0]['Message']) == "gallery name not found"):
        profile_pic_enroll(headers, payload)
        verify_res = verify_profile_picture(file, headers, payload)
        save_verify_confidance(verify_res)
        
except KeyError:
    tmp = 0
    sub_id = view_subject_id(headers, payload)
    verify_res = verify_profile_picture(file, headers, payload)
    #print(verify_res.content)
    tmp = save_verify_confidance(verify_res)

    if(tmp == 1):
        profile_pic_enroll(headers, payload)
    elif(sub_id == 1):
        print("This Profile Picture Already exist in gallary.")
        print("Try other..., Thank you\n\n")
    else:
        pass



