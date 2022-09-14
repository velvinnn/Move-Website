import pandas as pd
import random
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageFont, ImageDraw 
import textwrap
import math
import os
cards_file="static/cards.csv"
card_blank="static/card_blank.png"
fonts_file="static/arial.ttf"
cards_image="static/cards_image"
card_key_list=['measure','goal','days']

def read_action_cards():
    df=pd.read_csv(cards_file,dtype=str).values.tolist()
    
    return df
def read_card_info(card_id):
    #return the information of a certain card
    card_id=str(card_id)
    card_info={}
    card_file=pd.read_csv(cards_file, dtype=str)
    colnames=list(card_file)
    for index, row in card_file.iterrows():
        if row['card_id']==card_id:
            for colname in colnames:
                if pd.isna(row[colname]):
                    card_info[colname]=""
                else:
                    card_info[colname]=row[colname]
            # copy the measurement from measure 1 to measure 2 and 3 if speficied as empty
            for i in range(2,4):
                for key in card_key_list:
                        if pd.isna(row[key+str(i)]):
                            card_info[key+str(i)]=card_info[key+str(1)]

    return card_info

def card_directory(card_id):
    return "static/cards_image/"+str(card_id)+".png"
def get_all_cards_ids():
    #return the ids for all cards
    card_ids=[]
    with open(cards_file) as f:
        lines=f.readlines()[1:]
        for line in lines:
            if len(line)>3:
                card_ids.append(line.split(",")[0])
    return card_ids

def print_card(card_id):
    card_info=read_card_info(card_id)
    title_text = card_info["card type"]

    MAX_W, MAX_H = 500,1000
    card_image =  Image.new("RGBA",(MAX_W, MAX_H),"black")
    
    title_font = ImageFont.truetype(fonts_file, 90)
    subtitle_font = ImageFont.truetype(fonts_file, 30)
    text_font = ImageFont.truetype(fonts_file, 40)
    tiny_font=ImageFont.truetype(fonts_file, 30)
    image_editable = ImageDraw.Draw(card_image)

    #write title
    image_editable.text((300,50), "Card #"+str(card_id),font=tiny_font)

    #wrtie cards title
    current_h, pad = 150, 1
    para = textwrap.wrap(card_info["card type"], width=15)
    for line in para:
        w, h = image_editable.textsize(line, font=title_font)
        image_editable.text(((MAX_W - w) / 2, current_h), line, font=title_font)
        current_h += h + pad

    #wrtie cards name
    current_h, pad = 240, 1
    para = textwrap.wrap(card_info["name"], width=25)
    for line in para:
        w, h = image_editable.textsize(line, font=text_font)
        image_editable.text(((MAX_W - w) / 2, current_h), line, font=text_font)
        current_h += h + pad

    #entering the seprate line
    image_editable.line((0,340, 500, 340),  width=5)

    #wrtie cards content
    current_h, pad = 360, 0
    content_to_write=""
    for key_index in range(1,4):
        if len(card_info["miles"+str(key_index)])>0:
            content_to_write=card_info["miles"+str(key_index)]+" miles: "+card_info["descriptions"+str(key_index)]+"\n"
            para = textwrap.wrap(content_to_write, width=25)
            for line in para:
                w, h = image_editable.textsize(line, font=text_font)
                image_editable.text((30, current_h), line, font=text_font)
                current_h += h + pad
            current_h +=20
    
    #entering the seprate line
    image_editable.line((0,800, 500, 800),  width=5)
    
    #wrtie varification
    current_h, pad = 810, 1
    para = textwrap.wrap("Verify: "+card_info["verify"], width=35)
    for line in para:
        w, h = image_editable.textsize(line, font=tiny_font)
        image_editable.text((30, current_h), line, font=tiny_font)
        current_h += h + pad
    #entering the seprate line
    image_editable.line((0,930, 500, 930),  width=5)
    #wrtie reference page
    current_h, pad = 940, 1
    page_number=card_info["reference page"]
    para = textwrap.wrap(card_info["card type"]+" - "+card_info["category"]+"  (p."+str(page_number)+")", width=35)
    for line in para:
        w, h = image_editable.textsize(line, font=tiny_font)
        image_editable.text(((MAX_W - w) / 2, current_h), line, font=tiny_font)
        current_h += h + pad
    card_image.save(card_directory(card_id), quality=100, subsampling=0)
    return

def print_all_cards():
    card_ids=get_all_cards_ids()
    for id in card_ids:
        print_card(id)
    return

def draw_cards():
    f=[]
    for (dirpath, dirnames, filenames) in os.walk(cards_image):
        f.extend(filenames)
        break
    filename=random.choice(f)

    return "cards_image/"+filename#card_directory(draw_id)


