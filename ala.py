# -*- coding: utf-8 -*-
"""
his module provides functions for Automated Language Analysis (ALA), with a primary focus on the Slovenian language.
"""

import classla
import os
import shutil
import re
import pandas as pd
from tqdm import tqdm
from collections import Counter
import numpy as np

POS_tags=['ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET','INTJ', 'NOUN', 'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'X']
POS_tags_for_words=['ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET','INTJ', 'NOUN', 'NUM', 'PART', 'PRON', 'PROPN', 'SCONJ', 'VERB'] # POS_tags without X, PUNCT in SYM


def extract_genres_from_xml(input_folder,output_folder,genre):
    # use genre filter to extract xml files from input_folder to output_folder
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
    
    
    
def convert_xml_to_txt(input_folder,output_folder):    
    # read all xml files in input_folder and save them as txt in output_foled 
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
            cleaned_text=re.sub("&gt;","",cleaned_text) #včasih se not pojavijo te znaki   
            cleaned_text=re.sub(" \.",".",cleaned_text) #včasih se not pojavijo te znaki   
            if cleaned_text[-1] in [".","!","?"]:
                lines.append(cleaned_text)
        
        # Write the extracted words to the output file, one sentence per line
        if lines: 
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))          
    print("\nConversion completed!\n")

def clean_text(text,chars_to_remove = ['"', '«', '»']):
    pattern = '[' + re.escape(''.join(chars_to_remove)) + ']'
    text = re.sub(pattern, '', text) # delete chars_to_remove
    text = re.sub(r'\s+', ' ', text) # delete repeated spaces
    text = re.sub(r'([.!?])\1+', r'\1', text) # relete repeated punctuations        
    return text
    

def annotate_txt_with_classla(input_folder,output_folder):
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
    
def import_classla_xlsx_to_dataframe(input_folder):
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

def analyze_classla_xlsx(input_folder,output_folder):
    # loops through all xlsx files in input_folder
    # stores analysis in AnalyzedByClassla.xlsx in output_folder
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

    
def wTTR(token_string,window_width=500,downsampled_length=1000):
    token_list = token_string.split()
    def average_downsample(y_values):
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
    mean_TTR=np.mean(wTTR_list)
    std_TTR=np.std(wTTR_list)
    downsampled_list=average_downsample(wTTR_list)
    return mean_TTR, std_TTR, downsampled_list
