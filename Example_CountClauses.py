# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 21:01:21 2026

@author: jderganc
"""
import classla
import conllu
import module_syntactic_measures_t2024 as t2024
import module_slovenian_ala as si_ala


def three_line_aligned_wrapped(sent, max_width=160):
    # za izpis rezultatov štetja stavkov
    words   = [tok["form"]   for tok in sent]
    pos     = [tok["upos"]   for tok in sent]
    deprels = [tok["deprel"] for tok in sent]

    # compute column widths
    widths = [max(len(w), len(p), len(d)) for w, p, d in zip(words, pos, deprels)]
    cols = [(w.ljust(wd), p.ljust(wd), d.ljust(wd))
            for w, p, d, wd in zip(words, pos, deprels, widths)]

    lines = []
    cur_words, cur_pos, cur_deps = "", "", ""

    for wcol, pcol, dcol in cols:
        # length if we add this column (+1 for space if not first)
        sep = "" if cur_words == "" else " "
        new_len = len(cur_words) + len(sep) + len(wcol)

        if new_len > max_width and cur_words:
            # flush current block
            lines.append(cur_words.rstrip())
            lines.append(cur_pos.rstrip())
            lines.append(cur_deps.rstrip())
            lines.append("")  # blank line between wrapped lines
            cur_words, cur_pos, cur_deps = wcol, pcol, dcol
        else:
            cur_words += sep + wcol
            cur_pos   += sep + pcol
            cur_deps  += sep + dcol

    # flush remainder
    if cur_words:
        lines.append(cur_words.rstrip())
        lines.append(cur_pos.rstrip())
        lines.append(cur_deps.rstrip())

    return "\n".join(lines)


def primerjava_analiz(input_text:str)->str:
    doc = nlp(input_text)     # run the pipeline
    sentences = conllu.parse(doc.to_conll())
    output_text=""
    for sent in sentences:
            cisTercon=t2024.clauses_in_sent(sent)
            cisMDD1=si_ala.clauses_in_sent_MDD1(sent)
            cisMDD2=si_ala.clauses_in_sent_MDD2(sent)
            cis_result = "Terčon:"+ str(cisTercon)+"  MDD1:"+str(cisMDD1)+"  MDD2:"+str(cisMDD2)+ "\n"
            output_text = output_text + cis_result 
            output_text = output_text + three_line_aligned_wrapped(sent,80)+ "\n"+ "--------------------------------------\n" + "\n"  
            
    return output_text   


classla.download('sl')                            # download standard models for Slovenian, use hr for Croatian, sr for Serbian, bg for Bulgarian, mk for Macedonian
nlp = classla.Pipeline('sl') 

moj_tekst="To rekoč, so se otroci odpravili proti igrišču. Janez je ukazal metki oprati avto. Kaditi na balkonu je dovoljeno."  
rezultat=primerjava_analiz(moj_tekst)
print(rezultat)