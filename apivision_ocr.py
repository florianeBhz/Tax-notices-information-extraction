
import os
import io 
import pandas as pd
from google.cloud import vision
from enum import Enum
from PIL import Image, ImageDraw

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'ServiceAccountAPIToken.json'

def detect_text(path):
    """Returns for each document word, its content and bounding box"""
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    texts = response.text_annotations
    #print(response.full_text_annotation.pages[0].blocks[0])
    dict_res = {'Description':[],'Position':[]}

    for text in texts:
        vertices = (['({},{})'.format(vertex.x, vertex.y)
                for vertex in text.bounding_poly.vertices])
        vertices = ','.join(vertices)
        dict_res['Description'].append(text.description)
        dict_res['Position'].append(vertices)

    return dict_res 

    
def get_document_words_para_block(image_file):
    """Returns for each document word, its content, bounding box, 
    parent paragraph and parent block"""

    client = vision.ImageAnnotatorClient()

    with io.open(image_file, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    document = response.full_text_annotation

    words_para_blocks = {"num_word":[],
                            "word":[],
                            "para":[],
                            "block":[],
                            "bounds":[]}
    
    for page in document.pages:
        for num_block,block in enumerate(page.blocks):
            for num_paragraph,paragraph in enumerate(block.paragraphs):
                for num_word,word in enumerate(paragraph.words):
                    vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in word.bounding_box.vertices])
                    vertices = ','.join(vertices)
                    words_para_blocks["num_word"].append(num_word)
                    words_para_blocks["para"].append(num_paragraph)
                    words_para_blocks["block"].append(num_block)
                    words_para_blocks["bounds"].append(vertices)
                    text = ''
                    for symbol in word.symbols:
                        text += symbol.text
                    words_para_blocks["word"].append(text)

    # The list `bounds` contains the coordinates of the bounding boxes.
    return words_para_blocks


def get_ocr_outputs(images_dir = 'sample_100',output_dir='outputs/ocr_outputs/csv_files'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for img in os.listdir(images_dir):
        path = os.path.join(images_dir,img)
        result = get_document_words_para_block(path) #detect_text(path)
        df = pd.DataFrame.from_dict(result)
        outpath = os.path.join(output_dir,img.replace('jpg','csv'))
        df.to_csv(outpath)
        print("Saving {} content to 'outputs/ocr_outputs/csv_files/{}".format(img,img.replace('jpg','csv')))


############################# Visualize bounds on image ####################################


class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5

def draw_boxes(image, bounds, color):
    """Draw a border around the image using the hints in the vector list."""
    draw = ImageDraw.Draw(image)

    for bound in bounds:
        draw.polygon(
            [
                bound.vertices[0].x,
                bound.vertices[0].y,
                bound.vertices[1].x,
                bound.vertices[1].y,
                bound.vertices[2].x,
                bound.vertices[2].y,
                bound.vertices[3].x,
                bound.vertices[3].y,
            ],
            None,
            color,width=4
        )
    return image

def get_document_bounds(image_file, feature):
    """Returns document bounds given an image."""
    client = vision.ImageAnnotatorClient()

    bounds = []

    with io.open(image_file, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    document = response.full_text_annotation

    # Collect specified feature bounds by enumerating all document features
    for page in document.pages:
        for num_block,block in enumerate(page.blocks):
            for num_paragraph,paragraph in enumerate(block.paragraphs):
                for num_word,word in enumerate(paragraph.words):
                    for symbol in word.symbols:
                        if feature == FeatureType.SYMBOL:
                            bounds.append(symbol.bounding_box)

                    if feature == FeatureType.WORD:
                        bounds.append(word.bounding_box)

                if feature == FeatureType.PARA:
                    bounds.append(paragraph.bounding_box)

            if feature == FeatureType.BLOCK:
                bounds.append(block.bounding_box)

    # The list `bounds` contains the coordinates of the bounding boxes.
    return bounds

def render_doc_bounds(filein, fileout='annotation.jpg'):
    image = Image.open(filein)
    all_bounds = {'BLOCK':[],'PARA':[],'WORD':[]}

    bounds = get_document_bounds(filein, FeatureType.BLOCK)
    all_bounds['BLOCK'] = bounds

    bounds = get_document_bounds(filein, FeatureType.PARA)
    all_bounds['PARA'] = bounds

    bounds = get_document_bounds(filein, FeatureType.WORD)
    all_bounds['WORD'] = bounds
    
    if fileout != 0:
        draw_boxes(image, all_bounds['BLOCK'], "blue")
        draw_boxes(image, all_bounds['PARA'], "red")
        draw_boxes(image, all_bounds['WORD'], "yellow")
        image.save(fileout)
    
    return all_bounds

