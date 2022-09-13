from ast import mod
from calendar import week
from unicodedata import name
import numpy as np
import pandas as pd
import math
from cards import *
from helper_small import *

cards_dir="player/cards/"
steps_dir="player/weekly_steps/"
team_info_file="team/team info.csv"
city_distance_file="maps/city_dis.csv"
team_dir="team/"
maximum_weeks=30

x_min,x_max,y_min,y_max=-180,-60,15,73
start_location_id="28091"

def get_all_player_ids_in_team(team_id):
    return get_team_info(team_id)['player_ids']

def read_cities_dic(filename="maps/city_dic.csv"):
    df = pd.read_csv(filename)#.to_dict('list')
    return df


def read_cities(city_dic,team_id=0):
    city_ids=read_team_progress(team_id)["start location id"]
    x=[city_dic['x'][int(i)-1] for i in city_ids]
    y=[city_dic['y'][int(i)-1] for i in city_ids]
    return x,y

def read_city_info(city_dic,city_id):
    for i in city_dic.index:
        if city_dic['ID'][i]==int(city_id):
            return city_dic.loc[[i]].to_dict('list')
    return 
def find_customized_city_distance_between(cid1,cid2):
    message="There is no direct route between city #"+cid1+" and city #"+cid2
    category = "city_distance_False"
    dis=pd.read_csv(city_distance_file,dtype=str)
    city_dic=read_cities_dic()
    cinfo1,cinfo2=read_city_info(city_dic,cid1),read_city_info(city_dic,cid2)
    for i in dis.index:
        if dis['city_id1'][i]==cid1 and dis['city_id2'][i]==cid2:
            message="Between the current city ("+cinfo1['Name'][0]+") and the targt city ("+cinfo2['Name'][0]+"), the shorter route is "+dis['dis1'][i]+" miles, "
            message+="the longer route is "+dis['dis2'][i]+" miles. \n"
            if "nothing" not in cinfo2['bonus'][0]:
                message+="You will get "+cinfo2['bonus'][0]+" when you arrive "+cinfo2['Name'][0]
            category = "city_distance_True"
            return message,category
    return message,category
def city_dis(x1,y1,x2,y2):

    return np.sqrt((x1-x2)**2+(y1-y2)**2)*86
def xy_plot_to_map(x,y):

    return x*(x_max-x_min)+x_min,(1-y)*(y_max-y_min)+y_min

def find_nearest_city(x,y):
    x,y=xy_plot_to_map(x,y)
    [states,cities,lat,long,ids,points]=read_cities_dic(filename="maps/city_dic.csv")
    min_distance=100000
    target_id=0
    for i in range(len(states)):
        current_dis=city_dis(x,y,long[i],lat[i])
        if current_dis<min_distance:
            min_distance=current_dis
            target_id=i   
    return states[target_id],cities[target_id],lat[target_id],long[target_id],ids[target_id]

def new_miles(lat,long,team_id):
    city_dic=read_cities_dic()
    x,y=read_cities(city_dic,team_id=team_id)
    return np.sqrt(city_dis(long,lat,x[-1],y[-1]))*129/2.194

def get_team_info(team_id="1"):
    # return the user's information as a dictionary
    # maybe need to change filename, adding some directory
    team_id=str(team_id)
    team_info={}
    try:
        team_info=pd.read_csv(team_info_file,dtype=str)
        team_info=team_info[team_info['team_id']==team_id].to_dict('list')
        for key in team_info:
            team_info[key]=team_info[key][0]
        team_info['player_ids']=team_info['player_ids'].split(";")
    except:
       print("team id #"+str(team_id)+" information error")
    return team_info

def get_all_team_ids():
    #return the ids for all user
    team_ids=[]
    with open(team_info_file) as f:
        lines=f.readlines()[1:]
        for line in lines:
            if len(line)>3:
                team_ids.append(line.split(",")[0])
    return  team_ids

def if_team_exists(id):
    id=str(id)
    team_ids=get_all_user_ids()
    if id in team_ids:
        return True
    else:
        return False

def write_new_team_files(team_id):
    if not os.path.isfile(team_dir+team_id+".csv"):
        with open(team_dir+team_id+".csv","w") as f:
            f.write("the_ith_week,driver id,start location id,target location id,goal_miles,actual_miles,points,attendance\n")
            f.write("1,,29888,,,,,\n")
            for i in range(2,maximum_weeks+1):
                f.write(str(i)+",,,,,,,\n")
    return 

def read_team_progress(team_id):
    try:
        team_progress=pd.read_csv(team_dir+str(team_id)+".csv", dtype=str).to_dict('list')
        for key in team_progress:
            team_progress[key]=team_progress[key]
        return team_progress
    except:
        print('team #'+str(team_id)+' info is wrong!')
        return

def modify_team_progress(team_id,week_num,modify_key,modify_value):
    team_progress=pd.read_csv(team_dir+str(team_id)+".csv", dtype=str)
    for i in range(len(team_progress['the_ith_week'])):
        if int(team_progress.at[i,'the_ith_week'])==int(week_num):
            team_progress.at[i,modify_key]=modify_value
    team_progress.to_csv(team_dir+team_id+".csv", index=False,float_format='%.0f')
    return team_progress     

def read_team_progress_at(team_id,week_num=2):
    team_progress={}
    city_dic=read_cities_dic()
    try:
        if week_num>0:
            team_progress=pd.read_csv(team_dir+team_id+".csv",dtype=str,keep_default_na=False)
            team_progress=team_progress[team_progress['the_ith_week'] == str(week_num)].to_dict('list')
            for key in team_progress:
                team_progress[key]=str(team_progress[key][0])
                if ";" in team_progress[key]:
                    team_progress[key]=team_progress[key].split(';')
                elif 'card' in key:
                    if team_progress[key]:
                        team_progress[key]=[]
                    else:
                        team_progress[key]=[team_progress[key]]
            #print(team_progress)
            if team_progress["driver id"]:
                driver=get_user_info(team_progress["driver id"])
                team_progress["driver"]=driver["first_name"]+" "+driver["last_name"]
            else:
                team_progress["driver"]='not assigned yet'
            if team_progress["start location id"]: 
                team_progress["location"]=read_city_info(city_dic,team_progress["start location id"])['Name'][0]
            if team_progress["target location id"] and team_progress["target location id"]!='nan': 
                team_progress["destination"]=read_city_info(city_dic,team_progress["target location id"])['Name']
            else:
                team_progress["destination"]='not assigned yet'
            overall_progress=read_team_progress(team_id)
            #print(overall_progress["actual_miles"])
            team_progress["total_cities"]=len(set(overall_progress["start location id"]))
            team_progress["total_miles"]=np.nansum([float(i) for i in overall_progress["actual_miles"]])
            
            
            team_info=get_team_info(team_id)
            team_progress["team_name"]=team_info["team_name"]
            team_progress["player_ids"]=team_info["player_ids"]
            team_progress["game_start_date"]=team_info["game_start_date"]
    except:
        print("Team #"+str(team_id)+" has wrong info at week "+str(week_num))
    return team_progress

def generate_team_leader_board():
    team_ids=get_all_team_ids()
    result=[]
    for id in team_ids:
        week_num=get_team_week_num(id)
        result.append(read_team_progress_at(id,week_num))
    return result

def write_week_start_loc(team_id,week_num):
    if week_num>1:
        team_progress=read_team_progress_at(team_id,int(week_num)-1)
        team_progress_previous=read_team_progress_at(team_id,int(week_num)-2)
        if len(team_progress["goal_miles"]) > 0 and len(team_progress["actual_miles"]):
            if int(team_progress["goal_miles"])>int(team_progress["actual_miles"]):
                #failling to reach the goal
                modify_team_progress(team_id,week_num,"start location id",team_progress["start location id"])
                modify_team_progress(team_id,week_num-1,"points",int(team_progress_previous["points"]))
            else:
                modify_team_progress(team_id,week_num,"start location id",team_progress["target location id"])
                #getting the points
                states,cities,lat,long,ids,points=read_cities_dic()
                city_index=ids.index(team_progress["target location id"])
                new_points=points[city_index]
                modify_team_progress(team_id,week_num-1,"points",int(team_progress_previous["points"])+new_points)
    return

def update_team_info(team_id,week_num):
    write_week_start_loc(team_id,week_num)
    return


def get_all_team_ids():
    team_ids=[]
    with open(team_info_file) as f:
        lines=f.readlines()[1:]
        for line in lines:
            if len(line)>3:
                team_ids.append(line.split(",")[0])
    return team_ids

def get_team_week_num(team_id):
    # this the id for the previous week
    team_progress=read_team_progress(team_id)
    week_num=max([int(i) for i in team_progress['the_ith_week']])
    return week_num

#print(read_team_progress("1"))
#print(read_team_progress_at("1",week_num=2))
'''
write_new_team_files("2")
modify_team_progress("2",2,"start location id",125)
read_team_progress_at("2","2")

city_dic=read_cities_dic(filename="maps/city_dic.csv")
read_cities(city_dic,team_id=2)
'''

