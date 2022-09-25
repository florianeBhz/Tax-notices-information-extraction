import os 

RAW_DATA_DIR = 'sample_100'
CORRECTED_IMAGES_DIR = 'corrected_images'
OUTPUTS_DIR = 'outputs'
OCR_OUTPUTS = os.path.join(OUTPUTS_DIR,'ocr_outputs')
TESSERACT_OUTPUTS = os.path.join(OCR_OUTPUTS,'string_files')
API_VISION_OUTPUTS = os.path.join(OCR_OUTPUTS,'csv_files')
EXTRACTION_FILE = os.path.join(OUTPUTS_DIR,'extraction_info.csv')
