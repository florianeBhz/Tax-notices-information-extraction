from curses.ascii import isalpha
import spacy
import pandas as pd
import os
import re

# python3 -m spacy download fr_core_news_md

def check_class(csv_file='outputs/ocr_outputs/csv_files/9.csv',nb_blocks=10,key_word="avis d'impôt"):
    """
    This function searchs for a key word or set of key words in the first #nb_blocks  
    """
    boxes = pd.read_csv(csv_file)
    grouped = boxes.groupby(['block'])

    is_tax_notice = False 
    n = 0
    result_block = None

    while is_tax_notice == False and n < nb_blocks and n < len(grouped):
        block_text = ' '.join(boxes.groupby(['block']).get_group(n)['word'].tolist())
        if key_word in block_text.lower():
            is_tax_notice = True
            result_block = block_text
            break
        n += 1
    return (is_tax_notice,result_block)


def extract_from_csv(infile):
    boxes = pd.read_csv(infile)
    grouped = boxes.groupby(['block'])
    extraction_info = {}

    ####################################### TO DO ########################################## 
    n = 0
    while n < len(grouped):
        block_text = ' '.join(grouped.get_group(n)['word'].tolist())

        # nom , prénom
        if re.search(r"(M|Mme)[^\S]\S+[^\S]\S+",block_text):# (\w+) (\w+)"
            identity = block_text.strip().split()
            extraction_info["nom"] = identity[1]
            extraction_info["prenom"] = identity[2]
            extraction_info["adresse"] = ' '.join(identity[3:])
        
        # numéro fiscal
        if "numéro fip" in block_text.lower():
            vals = ' '.join(grouped.get_group(n+2)['word'].tolist())
            extraction_info["num_fiscal"] = vals

        # montant impôt
        if "somme qu'il vous reste à payer" in block_text.lower():
            vals = ' '.join(grouped.get_group(n).groupby('para').get_group(1)['word'].tolist())
            extraction_info["mtnt_impot"] = vals

        if "Plus de détails dans la ( les ) page ( s ) suivante ( s )" in block_text:
            vals = grouped.get_group(n+1)['word'].tolist()
            vals.extend(grouped.get_group(n+2)['word'].tolist())
            vals = ' '.join(vals)

            tmp = []
            for token in vals.split():
                if token.strip().isnumeric() or re.search('\d+\.\d+',token.strip()):
                    tmp.append(token)
                if token.strip().isalpha():
                    break
            extraction_info['revenu_fiscal_de_ref'] = ''.join(tmp[:-1])
            extraction_info['nb_parts'] = tmp[-1] if len(tmp) > 0 else ' '
                
        n += 1

    #########################################################################################
    return extraction_info


def process_document(document_name='9.csv',nb_blocks=10,key_word="avis d'impôt"):
    """
    given a document name, it checks if it is a tax notice;
     if true, then it performs extraction and return (True,Object); else it return (False,{})
    """
    # classification
    is_tax_notice,_ = check_class(csv_file='outputs/ocr_outputs/csv_files/'+document_name,nb_blocks=nb_blocks,key_word=key_word)
    extraction_obj = {}

    if is_tax_notice:
        # perform extraction
        extraction_obj = extract_from_csv(os.path.join('outputs/ocr_outputs/csv_files',document_name))

    return is_tax_notice,extraction_obj
