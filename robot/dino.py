# download DINO
import requests
import io
import os
url = "https://huggingface.co/sefaburak/dinov2-small-onnx/resolve/main/dinov2_vits14.onnx?download=true"
output_path = "dinov2_vits14.onnx"
if not os.path.exists(output_path):
    print('please wait ...')
    response = requests.get(url)
    if response.ok:
        file_like_object = io.BytesIO(response.content)
        with open(output_path, "wb") as f:
            f.write(file_like_object.getbuffer())
        print('downloaded')
    else:
        print('download failed')

# apply DINO
import numpy as np
import cv2
import time
net = cv2.dnn.readNetFromONNX("dinov2_vits14.onnx")
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
#net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
#net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

def dino(img):
    blob = cv2.dnn.blobFromImage(img, scalefactor=1/255.0, size=(224,224))
    net.setInput(blob)
    features = net.forward()[0]
    return features

def save_features(features,name):
    np.savetxt(name+'.npy', features)
    
def load_features(name):
    return np.loadtxt(name+'.npy')

def distance(features1, features2):
    return features1 @ features2

if __name__ == '__main__':
    img = cv2.imread('example.png')
    features = dino(img)
    print(features)
    features2 = dino(img)
    save_features(np.stack([features,features2],axis=0),'vocabulary')
