# -*- coding: utf-8 -*-
"""
Created on Sun Jun  1 11:56:40 2025

@author: Jure
"""
import module_slovenian_ala as si_ala
import matplotlib.pyplot as plt
import numpy as np
import os

# first we'll set the names of all folders
root_folder="Example_ccKres"
original_xml_folder=os.path.join(root_folder,"cckresV1_0")
literature_xml_folder=os.path.join(root_folder,"cckresV1_0_leposlovje")
txt_folder=os.path.join(root_folder,"cckresV1_0_leposlovje_txt")
classla_folder=os.path.join(root_folder,"cckresV1_0_Classla")

# now we'll extract literature texts from original_xml_folder and save them in literature_xml_folder
si_ala.extract_genre_from_corpus_xml(original_xml_folder,literature_xml_folder,genre="#SSJ.T.K.L")

# now we'll covert xml to text
si_ala.convert_corpus_xml_to_txt(literature_xml_folder,txt_folder)

# now we'll annotate files in txt_folder and save them as xlsx files in classla_folder
si_ala.annotate_txt_with_classla(txt_folder,classla_folder)

# now we'll analyze classla files and save results to root_folder
# the results are: 
# a) AnalyzedByClassla.xlsx file - file with all sentences and data
# b) ReportOnAnalysisOfClassla.txt - summary of analysis
si_ala.analyze_classla_xlsx(classla_folder,root_folder)


# next, we'll perform some more analysis and plot the results and save them in the root_folder

# first we'll import all analyzed results into one DataFrame for subsequent TTR analysis
df=si_ala.import_classla_xlsx_to_dataframe(classla_folder)

# next we'll plot windowed TTR for words and lemmas
window=500
# now we'll make a long text of all analyzed words and lemmas but we'll drop characters ['-','.', '?','!']
my_text = ' '.join(df["word"])
my_text=si_ala.clean_text(my_text,chars_to_remove = ['-','.', '?','!'])
mean_wTTR_words, std_wTTR_words, downsampled_wTTR_list_words = si_ala.wTTR_with_SD(my_text,window_width=500)
# now we'll make a long text of all analyzed lemmas but we'll drop characters ['-','.', '?','!']
my_text = ' '.join(df["lemma"])
my_text=si_ala.clean_text(my_text,chars_to_remove = ['-','.', '?','!'])
mean_wTTR_lemmas, std_wTTR_lemmas, downsampled_wTTR_list_lemmas = si_ala.wTTR_with_SD(my_text,window_width=500)
# now we'll plot how wTTR changes across the text
x_values = np.linspace(0, 1,len(downsampled_wTTR_list_words))
plt.plot(x_values, downsampled_wTTR_list_words, linewidth=1,label="words")
plt.plot(x_values, downsampled_wTTR_list_lemmas, linewidth=1,label="lemmas")
plt.title(f"wTTR of ccKres (window={window})")
plt.xlabel("% text")
plt.ylabel("TTR")
plt.xlim(0,1)
plt.ylim(0,1)
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.legend()
plt.savefig(os.path.join(root_folder,"wTTR_for_words_and_lemmas.png"))
plt.show()

# next we'll plot how mean_wTTR_lemmas and std_wTTR_lemmas change with window size
windows = list(range(50, 1001, 50))
mean_wTTR_list=[]
std_wTTR_list=[]
for window in windows:
    mean_wTTR_lemmas, std_wTTR_lemmas, downsampled_wTTR_list_lemmas = si_ala.wTTR_with_SD(my_text,window_width=window)
    mean_wTTR_list.append(mean_wTTR_lemmas)    
    std_wTTR_list.append(std_wTTR_lemmas)

x = np.array(windows)
y = np.array(mean_wTTR_list)
std = np.array(std_wTTR_list)
plt.plot(x,y, linewidth=2, label="mean")
plt.fill_between(x,y-std,y+std, alpha=0.5, label='±1 SD')
plt.xlabel("window width")
plt.ylabel("TTR")
plt.title("lemmas")
plt.legend()
plt.savefig(os.path.join(root_folder,"wTTR_for_lemmas_vs_window_size.png"))
plt.show()