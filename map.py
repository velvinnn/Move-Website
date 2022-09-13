#from flask_googlemaps import GoogleMaps,Map
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from teams import *
city_colors=["Red","Blue","Yellow","Green","pink","black"]
map_file="maps/game map.png"
def plot_map(ids=None,interested_lat=None,interested_long=None):
    city_dic=read_cities_dic()
    fig, ax = plt.subplots()
    #plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    img = plt.imread(map_file)
    ax.imshow(img)
    
    ax.axis("off")
    
    if ids is None:
        team_ids=get_all_team_ids()
    else:
        team_ids=ids
    for team_id in team_ids:
        x,y=read_cities(city_dic,team_id)
        ax.scatter(x,y,s=20,marker="^",c='green')
        ax.scatter(x[-1],y[-1],marker="^",s=40,c='green')
    if ids is None:
        plt.savefig("static/teams_all", bbox_inches="tight",dpi=300)
    else:
        plt.savefig("static/teams_"+team_id, bbox_inches="tight",dpi=300)
    plt.close()
    return
