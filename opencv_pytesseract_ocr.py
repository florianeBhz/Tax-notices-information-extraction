from distutils import extension
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pytesseract
import re
import os
import math
 

def correct_shift(image_path):
    image = cv2.imread(image_path)
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img_edges = cv2.Canny(img_gray, 100, 100, apertureSize=3)
    lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5)

    angles = []

    for [[x1, y1, x2, y2]] in lines:
        cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 3)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        angles.append(angle)

    angle = np.median(angles)
    #print(angle)
    #if angle < -45:
    #    angle = -(90 + angle)
    #else:
    #    angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated

def correct_images(images_dir='sample_100',output_dir='corrected_images'):
    for img in os.listdir(images_dir):
        name = img
        res = correct_shift(os.path.join(images_dir,img))
        if not cv2.imwrite(os.path.join(output_dir,name),res):
            raise Exception("Could not write image "+name)


def get_document_content(image):
    img = cv2.imread(image)
    st = pytesseract.image_to_string(img)
    return st 
    
def save_contents(images_dir='corrected_images',txt_dir='outputs/ocr_outputs/string_files'):
    for image in os.listdir(images_dir):
        name = image.split('.')[0]
        img_path = os.path.join(images_dir,image)
        st = get_document_content(img_path)
        with open(os.path.join(txt_dir,name+'.txt'), 'w+') as f:
            f.write(st) 
            print(image +" content saved to "+txt_dir)

def get_ocr_outputs(raw_images_dir='sample_100',processed_images_dir='corrected_images',
    txt_dir='outputs/ocr_outputs/string_files'):
    # rectify rotation with openCV
    correct_images(images_dir=raw_images_dir,output_dir=processed_images_dir)
    # get and save text content with pytesseract
    save_contents(images_dir=processed_images_dir,txt_dir=txt_dir)



"""
processor = Preprocess_image()
processor.set_template('sample_100/9.jpg')
img = processor.set_image('sample_100/2.jpg')

match = processor.deskew(r'corrected_images')
plt.figure()
plt.imshow(match)
plt.show()
"""