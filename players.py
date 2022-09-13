from calendar import week
from genericpath import isfile
import numpy as np
from cards import *
from helper_small import *
from teams import *
from cards import *
cards_dir="player/cards/"
report_dir="player/report/"
steps_dir="player/weekly_steps/"
miles_dir="player/miles/"
team_info_file="team/team info.csv"
def write_weekly_steps(user_id,weekly_total):
    with open(steps_dir+user_id+".csv","w") as f:
        f.write("week #,total steps\n")
        for i in range(len(weekly_total)):
            f.write(str(i+1)+","+str(weekly_total[i])+"\n")
    return
def write_weekly_miles(user_id,miles,week_num):
    if not os.path.exists("player/miles/"+str(user_id)+".csv"):
        with open("player/miles/"+str(user_id)+".csv","w") as f:
            f.write("week #,miles\n")
    with open("player/miles/"+str(user_id)+".csv","a") as f:
        f.write(str(week_num)+","+str(miles)+"\n")
    return

def write_new_player_cards(user_id):
    if not os.path.isfile(cards_dir+user_id+".csv"):
        with open(cards_dir+user_id+".csv","w") as f:
            f.write("week #,card ids\n")
            for i in range(1,31):
                f.write(str(i)+",\n")
    return
def write_new_player_miles(user_id):
    if not os.path.isfile(miles_dir+user_id+".csv"):
        with open(miles_dir+user_id+".csv","w") as f:
            f.write("week #,miles\n")
            for i in range(1,31):
                f.write(str(i)+",\n")
    return
def write_new_player_steps(user_id):
    if not os.path.isfile(steps_dir+user_id+".csv"):
        with open(steps_dir+user_id+".csv","w") as f:
            f.write("week #,total steps\n")
            for i in range(1,31):
                f.write(str(i)+",\n")
    return
def update_player_cards(user_id,card_id,week_num):
    write_new_player_cards(user_id)
    all_card_ids=get_all_cards_ids()
    user_id,card_id=str(user_id),str(card_id)
    current_cards,previous_cards=read_cards(user_id,week_num=week_num)
    if not card_id in all_card_ids:
        print("Invalid card id! Assignment Failure.")
        return False
    if card_id in current_cards:
        return True
    to_write=[]
    with open(cards_dir+user_id+".csv") as f:
        lines=f.readlines()
        for line in lines:
            words=line.split(",")
            if words[0]==str(week_num):
                line=line.replace("\n",card_id+",\n")
            to_write.append(line)
    with open(cards_dir+user_id+".csv","w") as f:
        for line in to_write:
            f.write(line)
    return True

def read_cards(user_id,date=None,week_num=None):
    if week_num is None:
        week_num=get_team_week_num(user_id,date=date)
    current_cards,previous_cards=[],[]
    if os.path.isfile(cards_dir+user_id+".csv"):
        with open(cards_dir+user_id+".csv") as f:
            lines=f.readlines()[1:]
            for line in lines:
                line=line.replace("\n","")
                words=line.split(",")
                if int(words[0])<week_num:
                    for w in words[1:]:
                        if len(w)>0:
                            previous_cards.append(w)
                elif int(words[0])==week_num:
                    for w in words[1:]:
                        if len(w)>0:
                            current_cards.append(w)
    return current_cards,previous_cards



def get_all_palyer_ids():
    result=[]
    team_ids=get_all_team_ids()
    for id in team_ids:
        player_ids=get_all_player_ids_in_team(id)
        for pid in player_ids:
            result.append(pid)
    return result

def get_player_accumulative_steps(player_id,week_num):
    total_steps=0
    current_steps=0
    steps=pd.read_csv(steps_dir+str(player_id)+".csv")
    for index in steps.index:
        if int(steps['week #'][index])<=week_num:
            total_steps+=steps['total steps'][index]
        if int(steps['week #'][index])==week_num:
            current_steps+=steps['total steps'][index]
    return total_steps,current_steps

def get_player_accumulative_miles(player_id,week_num):
    total_miles=np.zeros(24)
    current_miles=0
    write_new_player_miles(player_id)
    miles=pd.read_csv(miles_dir+str(player_id)+".csv")
    for index in miles.index:
        if int(miles['week #'][index])<=week_num:
            total_miles[miles['week #'][index]]=miles['miles'][index]
        if int(miles['week #'][index])==week_num:
            current_miles=miles['miles'][index]
    return np.sum(total_miles),current_miles

def get_player_progress(player_id,week_num):
    player_info=get_user_info(player_id)
    player_info['name']=player_info["first_name"]+" "+player_info["last_name"]
    if week_num>0:
        player_info["miles"],player_info["current_miles"]=get_player_accumulative_miles(player_id,week_num)
    else:
        player_info["miles"],player_info["current_miles"]=0,0
    player_info["commitment_cards"]=[]
    for i in range(1,int(week_num)+1):
        if os.path.exists("static/commitment_cards/"+player_id+"_week"+str(i)+".png"):
            player_info["commitment_cards"].append(player_id+"_week"+str(i))
    team_ids=get_all_team_ids()
    for team_id in team_ids:
        all_player_ids=get_all_player_ids_in_team(team_id)
        if player_id in all_player_ids:
            team_info=get_team_info(team_id)
            player_info['game_start_date']=team_info['game_start_date']
    return player_info
def get_players_progress(team_id=None):
    result=[]
    if team_id is None:
        team_ids=get_all_team_ids()
    else:
        team_ids=[team_id]

    for t_id in team_ids:
        player_ids=get_all_player_ids_in_team(t_id)
        team_info=get_team_info(t_id)
        week_num=get_team_week_num(t_id)
        if week_num>1:
            team_progress=read_team_progress_at(t_id,week_num)
        else:
            team_progress={}
            team_progress['driver id']=''
        for player_id in player_ids:
            player_info=get_player_progress(player_id,week_num)
            #print(player_info)
            player_info['team_id']=t_id
            player_info['team_name']=team_info['team_name']
            result.append(player_info)
    return result

def update_team_miles(team_id,week_num):
    pids=get_all_player_ids_in_team(team_id)
    avg_miles=0
    for pid in pids:
        progress=get_player_progress(pid,week_num)
        avg_miles+=int(progress["current_miles"])
    avg_miles=avg_miles/len(pids)
    modify_team_progress(team_id,week_num,'actual_miles',str(int(avg_miles)))
    return

def update_team_at_week(team_id,week_num):
    error_message=""
    team_info=read_team_progress_at(team_id,week_num)
    if team_info["target location id"]:
        return "Team information in previous weeks is missing."
    if team_info['actual_miles']:
        # update all the player miles in the team
        player_ids=get_all_player_ids_in_team(team_id)
        most_recent_update_date=get_date_time(team_info['game_start_date'])+timedelta(days=week_num*7-1)
        for player_id in player_ids:
            user_info=get_user_info(player_id)
            if check_synced(user_info,date=most_recent_update_date):
                weekly_update_player_miles(player_id,week_num)
            else:
                error_message+="Error! Player #"+str(player_id)+" does not has his/her fitbit synced yet."
        if len(error_message)==0:
            # update the team average miles
            update_team_miles(team_id,week_num)
            #deciding the team start location for the next week
            write_week_start_loc(team_id,week_num+1)
            
    return error_message

def get_team_miles(team_id,week_num):
    player_ids=get_all_player_ids_in_team(team_id)
    total_miles=0
    for id in player_ids:
        total_miles+=get_player_accumulative_miles(id,week_num)[1]
    total_miles=total_miles/len(player_ids)
    total_miles=str(int(total_miles))
    modify_team_progress(team_id,week_num,"player_miles",total_miles)
    return 
#read_player_fitbit_data("1","2",end_date=None)
#_,___=get_player_accumulative_miles("1",2)
#print(_)

'''
get_all_palyer_ids()
'''
#update_team_miles("1",2)

#update_player_cards("8",13)