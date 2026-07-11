# -*- coding: utf-8 -*-
"""
This module provides some useful functions for Automated Language Analysis (ALA), with a primary focus on the Slovenian language.

The functions are divided into sections:
    - functions for dealing with corpus xml files
    - functions for dealing with classla annotation and Excel xlsx files
    - functions for ALA measures
    - various utilities

"""


import classla
import os
import shutil
import re
from collections import Counter
import pandas as pd
from tqdm import tqdm
import numpy as np


POS_tags: list[str] = ['ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET','INTJ', 'NOUN', 'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X']
POS_tags_for_words: list[str] = ['ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET','INTJ', 'NOUN', 'NUM', 'PART', 'PRON', 'PROPN', 'SCONJ', 'VERB'] # POS_tags without X, PUNCT in SYM


########################################
## begin: functions for dealing with corpus xml files
#######################################

def extract_genre_from_corpus_xml(input_folder: str, output_folder: str, genre: str) -> None:
    # use genre filter to extract xml files from input_folder to output_folder
    # corpora xml should be encoded in XML TEI format see
    # it was tested on ccKres 1.0 Slovenian corpus, http://hdl.handle.net/11356/1034
    # 
    """
    leposlovje:genre="#SSJ.T.K.L"
    strokovno:genre="#SSJ.T.K.S"
    periodicno:genre="#SSJ.T.P"
    internet:genre="#SSJ.I"
    drugo:genre="#SSJ.T.D"
    """
    os.makedirs(output_folder, exist_ok=True)
    # Loop through all XML files in the input folder
    print(f"Extraction of xml files with genre: {genre} started.")
    
    xml_files = [f for f in os.listdir(input_folder) if f.endswith(".xml")]
    genre_file_counter=0
    for filename in tqdm(xml_files):
       file_path=os.path.join(input_folder, filename)
       with open(file_path, "r", encoding="utf-8") as file:
           content = file.read()
           if genre in content:
               shutil.copy(file_path, output_folder)
               genre_file_counter += 1     
    print(f"\nExtraction complete. ({len(xml_files)} input files, {genre_file_counter} output files).\n")
        
    
def convert_corpus_xml_to_txt(input_folder: str, output_folder: str) -> None:    
    # read all xml files in input_folder and save them as txt in output_folder 
    # corpora xml should be encoded in XML TEI format see
    # it was tested on ccKres 1.0 Slovenian corpus, http://hdl.handle.net/11356/1034
    os.makedirs(output_folder, exist_ok=True)
    xml_files = [f for f in os.listdir(input_folder) if f.endswith(".xml")]
    
    print("Conversion of xml files to txt files started.")
    
    for filename in tqdm(xml_files):
        input_file = os.path.join(input_folder,filename)
        output_file = os.path.join(output_folder,filename[:-4]+".txt")
        
        with open(input_file, "r", encoding="utf-8") as f:
            text = f.read()
        
        # Find all sentences (<s>...</s>) in the text
        sentences = re.findall(r"<s>(.*?)</s>", text, re.DOTALL)
        
        lines = []
        for sentence in sentences:
            # Remove all tags including brackets
            cleaned_text = re.sub(r"<[^>]+>", "", sentence)
            # Normalize spaces
            cleaned_text = " ".join(cleaned_text.split())
            cleaned_text=re.sub("&lt;","",cleaned_text)
            cleaned_text=re.sub("&gt;","",cleaned_text) #sometimes these characters appear inside   
            cleaned_text=re.sub(r" \.",".",cleaned_text) #sometimes these characters appear inside   
            if cleaned_text[-1] in [".","!","?"]:
                lines.append(cleaned_text)
        
        # Write the extracted words to the output file, one sentence per line
        if lines: 
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))          
    print("\nConversion completed!\n")


########################################
## end: functions for dealing with corpus xml files
#######################################
   

########################################
## begin: functions for dealing with classla annotation and Excel xlsx files 
#######################################

def annotate_txt_with_classla(input_folder: str, output_folder: str) -> None:
    # Reads txt files from input_folder and analyzes them with classla.
    # The results will be saved as .xlsx files in the output_folder
    # The xlsx files will contain columns "word", "lemma", "pos" and "deprel"
    # Sentences will be separated by empty rows.
    os.makedirs(output_folder, exist_ok=True)

    # Preberemo datoteke iz text_path
    files_to_process = [f for f in os.listdir(input_folder) if f.endswith(".txt")]

    classla.download('sl')  # download standard models for Slovenian, use hr for Croatian, sr for Serbian, bg for Bulgarian, mk for Macedonian
    nlp = classla.Pipeline('sl',use_gpu=True) # initialize the default Slovenian pipeline, use hr for Croatian, sr for Serbian, bg for Bulgarian, mk for Macedonian

    print("Classla annotation started.")
    for file_to_process in tqdm(files_to_process):
        with open(os.path.join(input_folder,file_to_process), encoding='utf-8') as f:
           text = f.read()
        text=clean_text(text)
        doc = nlp(text)

        results = []
        for sentence in doc.sentences:
            for word in sentence.words:
                results.append({
                    "word": word.text,
                    "lemma": word.lemma,
                    "pos": word.pos,
                    "deprel": word.deprel
                })
            results.append({"word":"-","lemma":"-","pos":"-","deprel":"-"}) #dashes are markers for  end-of-sentence 
        df = pd.DataFrame(results)                         
        basename = os.path.splitext(os.path.basename(file_to_process))[0]
        df.to_excel(os.path.join(output_folder,basename+'.xlsx'), index=False)
    print("\nClassla annotation finished.\n")
    
def import_classla_xlsx_to_dataframe(input_folder: str) -> pd.DataFrame:
    # Imports all xlsx classla files from input_folder and combines them into one dataframe
    # The xlsx files and thus also the dataframe have columns "word", "lemma", "pos" and "deprel"
    files_to_process = [f for f in os.listdir(input_folder) if f.endswith(".xlsx")]
    combined_df = pd.DataFrame()
    print("Importing started.")
    for file in tqdm(files_to_process):
        df = pd.read_excel(os.path.join(input_folder,file) , engine='openpyxl', dtype="string",keep_default_na=False)
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    print("\nImporting finished.\n")
    return combined_df

def analyze_classla_xlsx(input_folder: str, output_folder: str) -> None:
    # loops through all xlsx files in input_folder
    # stores analysis in AnalyzedByClassla.xlsx in output_folder
    # also makes a txt report in the output_folder
    xlsx_files = [f for f in os.listdir(input_folder) if f.endswith('.xlsx')]        
    rows = []    
    for file_name in tqdm(xlsx_files):

        df = pd.read_excel(os.path.join(input_folder,file_name), engine='openpyxl', dtype="string",keep_default_na=False)
        df_length=len(df)
        
        sentence_counter=0
        sentence_start=0
                
                
        for i in range(df_length):
            # loops through rows and looks for sentences, clauses ... 
            current_pos=df.loc[i, "pos"]
                 
            if current_pos=="-": 
                # sentences are delimited by rows with dashes
                # this means that the previous sentence ended 
                sentence_counter += 1        
                
                # get the list of words in the sentence and join them into a string                                                
                sentence_word_list  = df["word"].iloc[sentence_start:i].tolist()     
                sentence=' '.join(sentence_word_list)    
                
                # get a list of pos tags in the sentence and make a dictionary of their counts
                sentence_pos_list = df["pos"].iloc[sentence_start:i].tolist()                            
                tag_counts = Counter(sentence_pos_list)
                tag_counts_dict = {tag: tag_counts.get(tag, 0) for tag in POS_tags}
                
                # number of words is the number of pos tags that are POS_tags_for_words
                n_words = sum(tag_counts[tag] for tag in POS_tags_for_words)
                
                # sentence id is filename + sentence counter
                sentence_id= file_name[:-5].ljust(len(file_name)-4)+"-"+str(sentence_counter).rjust(3)
                
                new_row={"ID":sentence_id,"Sentence":sentence,"N words":n_words}                        
                new_row.update(tag_counts_dict)
                rows.append(new_row)
                #print(new_row)
                sentence_start=i+1 
                
                
    df_results = pd.DataFrame(rows)      
    df_results.to_excel(os.path.join(output_folder,"AnalyzedByClassla.xlsx"), index=False)
    
    # now make a report and save it
    report_text=""
    report_text = report_text + "N sentences: " + str(len(df_results)) + "\n"
    report_text = report_text + "N words: " + str(df_results['N words'].sum()) + "\n"
    report_text = report_text + "Average words per sentence: " + str(round(df_results['N words'].mean(),1)) + "\n"
    report_text = report_text + "SD N words per sentence: " + str(round(df_results['N words'].std(),1)) + "\n"
  
    sums = df_results[POS_tags_for_words].sum()
    total = sums.sum()
    percentages = (sums / total * 100).round(1)
    
    report_text=report_text+" \t"+"\t".join(POS_tags_for_words)+"\n"
    report_text=report_text+"N\t"+"\t".join(str(int(s)) for s in sums)+"\n"
    report_text=report_text+"%\t"+"\t".join(f"{p:.2f}" for p in percentages)+"\n"
        
    with open(os.path.join(output_folder,"ReportOnAnalysisOfClassla.txt"), "w") as file:
        file.write(report_text)

########################################
## end: functions for dealing with classla annotation and Excel xlsx files 
#######################################

########################################
## begin: functions for ALA measures
#######################################


def wTTR_with_SD(text_string: str, window_width: int = 500, downsampled_length: int = 1000) -> tuple[float, float, list[float]]:
    # function for calculating windowed TTR and its standard deviation
    # it also returns a downsampled list of values showing how TTR as window passes through the text
    token_list = text_string.split()
    def average_downsample(y_values: list[float]) -> list[float]:
        y_values = np.array(y_values)
        n = len(y_values)
        
        # Compute the size of each block
        block_size = n / downsampled_length

        averaged = [
            y_values[int(i * block_size):int((i + 1) * block_size)].mean()
            for i in range(downsampled_length)
        ]
        
        return averaged
    type_set={}    
    wTTR_list=[]
    for i in range(len(token_list)-window_width):
        current_token_window_list=token_list[i:i+window_width]             
        type_set=set(current_token_window_list)        
        wTTR_list.append(len(type_set)/window_width)
    mean_TTR = float(np.mean(wTTR_list))
    std_TTR = float(np.std(wTTR_list))
    downsampled_list=average_downsample(wTTR_list)
    return mean_TTR, std_TTR, downsampled_list

def clauses_in_sent_MDD1(sentence) -> int: 
    # calculates number of clauses according to Marvin Derganc & Derganc 2026
    # sentence should be of type "conllu sentence object", i.e., list[dict[str, str]]
    # the method takes into accound dependency relations
    clauses_counter = 0
    for tok in sentence:
        if (tok["upos"]=="AUX"  and tok["deprel"]=="cop") or \
           (tok["upos"]=="VERB" and tok["deprel"]!="xcomp"):
            clauses_counter += 1
    return clauses_counter    


def clauses_in_sent_MDD2(sentence):
    # calculates number of clauses according to Marvin Derganc & Derganc 2026
    # sentence should be of type "conllu sentence object", i.e., list[dict[str, str]]
    # the method does not take into accound dependency relations    
    def is_verb_but_not_inf_or_sup(tok):
        feats = tok.get("feats")
    
        if isinstance(feats, dict):
            verb_form = feats.get("VerbForm")
        elif isinstance(feats, str):
            # fallback if feats is stored as a string like "VerbForm=Inf|..."
            verb_form = None
            for part in feats.split("|"):
                if part.startswith("VerbForm="):
                    verb_form = part.split("=", 1)[1]
                    break
        else:
            verb_form = None
    
        return (
            tok.get("upos") == "VERB"
            and verb_form not in {"Inf", "Sup"}
        )
    
    clauses_counter = 0
    for tok in sentence:
        if (tok["upos"]=="AUX"  and tok["deprel"]=="cop") or is_verb_but_not_inf_or_sup(tok):         
            clauses_counter += 1
    return clauses_counter    




########################################
## end: functions for ALA measures
#######################################


########################################
## begin: various utilities
#######################################

def clean_text(text: str, chars_to_remove: list[str] = ['"', '«', '»']) -> str:
    pattern = '[' + re.escape(''.join(chars_to_remove)) + ']'
    text = re.sub(pattern, '', text) # delete chars_to_remove
    text = re.sub(r'\s+', ' ', text) # delete repeated spaces
    text = re.sub(r'([.!?])\1+', r'\1', text) # delete repeated punctuations        
    return text

    

########################################
## end: various utilities
#######################################
