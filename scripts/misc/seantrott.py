# -*- coding: utf-8 -*-
"""seantrott.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ya-uFjkyXEVbsnc4naKWm9s1hoASvOC4
"""

import requests
import pandas as pd
import io
import numpy as np
import os
import warnings

#!pip install fuzzywuzzy
import fuzzywuzzy

from fuzzywuzzy import fuzz
import re

warnings.filterwarnings("ignore")
import spacy

from fuzzywuzzy import process


nlp = spacy.load("en_core_web_sm")

URL = "https://raw.githubusercontent.com/seantrott/raw-c/main/data/processed/raw-c.csv"
download = requests.get(URL).content
df = pd.read_csv(io.StringIO(download.decode('utf-8')),sep = ',')


df_dash = df[['word', 'sentence1', 'sentence2', "Class"]]

df1 = df_dash[['word', 'sentence1', 'Class']]
df1.columns =  ['word', 'sent', 'class']
df1["index"] = df1.groupby("word").cumcount()*2

df2 =  df_dash[['word', 'sentence2', 'Class']]
df2.columns =  ['word', 'sent', 'class']
df2["index"] = df2.groupby("word").cumcount()*2+1

df_final = pd.concat([df1, df2])
df_final = df_final.sort_values(by = ['word', 'index'], ascending = [True, True])

df_final["identifier"] = df_final["word"]+"-"+df_final["index"].astype(str)

df_odd = df_final[1::2]
df_odd.columns = ["word2", "sent2", 'class2', "index2", "identifier2"]
df_even = df_final[::2]
df_even.columns = ["word1", "sent1", "class1", "index1", "identifier1"]
df_final = pd.concat([df_even, df_odd], axis=1)

df_final = df_final[["word2", "sent2", "identifier2", 'class2', "sent1", "identifier1", 'class1', 'index1', 'index2']]
df_final_next_stage = df_final.rename(columns={"word2":"lemma"})

df_final = df_final_next_stage


df_final["judgment"] = df["same"].values.tolist()

df_final = df_final[['lemma', 'identifier2', 'identifier1', 'judgment']]

df_final["annotator"] = " "
df_final["comment"] = df['ambiguity_type']

df_final = df_final[["identifier1", "identifier2", "annotator", "judgment", "comment", "lemma"]]


for i in list(df_final["lemma"].value_counts().index):
    df_temp = df_final[df_final["lemma"]==i]
    numpy_df = df_temp.to_numpy()
    header = list(df_temp.columns)
    numpy_df = np.vstack([header, numpy_df])
    if not os.path.exists(i):
        os.mkdir(i)
    np.savetxt(i+"/judgments.csv", numpy_df,fmt='%s', delimiter='\t')


df1 = df_final_next_stage[['lemma', 'sent1', 'class1', 'identifier1', 'index1']]
df1.columns =  ['word', 'sent', 'pos', 'identifier', 'index']
df2 = df_final_next_stage[['lemma', 'sent2', 'class2', 'identifier2', 'index2']]
df2.columns =  ['word', 'sent', 'pos', 'identifier', 'index']

df_final = pd.concat([df1, df2])


df_final = df_final.reset_index(drop = True)

tag = ''
def get_indices_of_tags(sentence, word):
   i = sentence.split(" ")
   tag = process.extractOne(word, i)
   tag = tag[0]
   #print(tag)
   tag = re.sub('\W+', '', tag)
   return(str(sentence.find(tag))+":"+str(sentence.find(tag)+len(tag)))

def get_target(sentence, word):
   tok = sentence.split(" ")
   tag = process.extractOne(word, tok)
   tag = tag[0]
   #print(tag)
   for i in tok:
     if tag == i:
       ind = tok.index(i)
   return ind

df_final["indexes_target_token"] = df_final.apply(lambda x: get_indices_of_tags(x.sent, x.word), axis=1)

df_final['indexes_target_token_tokenized'] = df_final.apply(lambda x: get_target(x.sent, x.word), axis=1)



def get_indices_of_sent(sentence):
    return "0:"+str(len(sentence))

df_final["indexes_target_sentence"] = df_final["sent"].apply(get_indices_of_sent)

df_final = df_final.rename(columns = {"sent":"context", "word":"lemma"})

df_final['description'] = " "
df_final['date'] = " "
df_final['grouping'] = " "

df_final = df_final[['lemma', 'pos', 'date', 'grouping', 'identifier', 'description', 'context', 'indexes_target_token', 'indexes_target_sentence', 'indexes_target_token_tokenized', 'index' ]]



df_final['context_tokenized'] = df_final['context']

def get_len_tok(sentence):
  return "0:"+str(len(sentence.split(" ")))

df_final['indexes_target_sentence_tokenized'] = df_final["context_tokenized"].apply(get_len_tok)

lem = ''
def lemmatizr(sent):
  doc = nlp(sent)
  for i in doc:
    lem += i.lemma_
    return lem

df_final['context_lemmatized'] = df_final["context_tokenized"].apply(lambda row: " ".join([w.lemma_ for w in nlp(row)]))

df_final['context_pos'] = df_final["context_tokenized"].apply(lambda row: " ".join([w.pos_ for w in nlp(row)]))

final_df = df_final[['lemma', 'pos', 'date', 'grouping', 'identifier', 'description', 'context', 'indexes_target_token', 'indexes_target_sentence', 'context_tokenized', 'indexes_target_token_tokenized', 'indexes_target_sentence_tokenized', 'context_lemmatized', 'context_pos', 'index']]

final_df = df_final.sort_values(by = ['lemma', 'index'], ascending = [True, True]).drop("index", axis=1)

final_df = final_df.reset_index(drop = True)



final_df1 = final_df.explode("description")



for i in list(final_df["lemma"].value_counts().index):
    df_temp = final_df[final_df["lemma"]==i]
    numpy_df = df_temp.to_numpy()
    header = list(df_temp.columns)
    numpy_df = np.vstack([header, numpy_df])
    if not os.path.exists(i):
        os.mkdir(i)
    np.savetxt(i+"/uses.csv", numpy_df,fmt='%s', delimiter='\t')

