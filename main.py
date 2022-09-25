import imp
import opencv_pytesseract_ocr
import apivision_ocr 
import extractor  
import config
import os
import pandas as pd

def pipeline(raw_data_dir = config.RAW_DATA_DIR,ocr_vision_outputs_dir=config.API_VISION_OUTPUTS,
    ocr_tesseract_outputs_dir=config.TESSERACT_OUTPUTS, final_output=config.EXTRACTION_FILE):
    # 1 . OpenCV rotation correction + pytesseract OCR and saving results txt files
    #opencv_pytesseract_ocr.get_ocr_outputs(raw_images_dir='sample_100',processed_images_dir='corrected_images',
    #    txt_dir='outputs/ocr_outputs/string_files')
    # OR 

    # 2 . Using Google Cloud API Vision OCR on raw images and saving results csv files
    apivision_ocr.get_ocr_outputs(images_dir=raw_data_dir,output_dir=config.API_VISION_OUTPUTS)

    # AND 

    # 3 . Process documents (csv files) 
    #  - Classify documents : If it is a tax document , then perform extraction 
    #  - Extract information from ocr outputs and saving in a single csv file for analysis.

    extractions = {"id_doc":[],
                    "nom":[],
                    "prenom":[],
                    "adresse":[],
                    "num_fiscal":[],
                    "mtnt_impot":[],
                    "revenu_fiscal_de_ref":[],
                    "nb_parts":[]}
    
    for doc in os.listdir(ocr_vision_outputs_dir):
        is_tax_notice,info = extractor.process_document(document_name=doc)
        if is_tax_notice:
            info['id_doc']=doc.replace('csv','jpg')
            for k in extractions.keys():
                if k in info.keys():
                    extractions[k].append(info[k])
                else:
                    extractions[k].append("")

    df = pd.DataFrame.from_dict(extractions)
    df.to_csv(final_output)
    print("All extractions saved to {}".format(final_output))


if __name__ == "__main__":
    pipeline()