import pandas as pd
import random
import numpy as np
import os
cards_file="static/cards.csv"
card_blank="static/card_blank.png"
fonts_file="static/arial.ttf"
cards_image="static/cards_image"
card_key_list=['measure','goal','days']

def read_action_cards():
    df=pd.read_csv(cards_file,dtype=str).values.tolist()    
    return df

def draw_cards():
    f=[]
    for (dirpath, dirnames, filenames) in os.walk(cards_image):
        f.extend(filenames)
        break
    random.Random(1).shuffle(f)
    f=["cards_image/"+filename for filename in f]
    return f
    #return "cards_image/"+filename#card_directory(draw_id)

