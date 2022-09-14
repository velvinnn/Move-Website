import re
import os
import stat
from typing import MappingView
from flask import Flask,render_template,request,redirect, url_for,session,make_response,jsonify,flash
import random
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_util_js import FlaskUtilJs
from map import *
from teams import *
from helper_small import *
from cards import *
from players import *
from plot_player import *
outlook_sender_email ="fitbit.test.motivate@outlook.com" 
gmail_sender_email ="fitbit.test.motivate@gmail.com"
password="s021mds./02la" # the passwords are the same for both accounts
'''
google_map_key= 'AIzaSyBV1VyYB9QHFM_LZ4VOuln35bGiw_xIza4'
app.config['GOOGLEMAPS_KEY'] =google_map_key
GoogleMaps(app)
'''

app = Flask(__name__)
fujs = FlaskUtilJs(app)
app.secret_key = 'DSIWNKLkjxiawsjd23,;esdw'  

#return the webpage for teams
def team_webpage(cards_drawn=[],team_id=None,interested='False',interested_city={},marker_pos={},card_challenge_id="",parcitipant_data="None"):
    #return the webpage of the team
    if len(marker_pos)==0:
        marker_pos={'x':0,'y':0}
    if len(cards_drawn)==0:
        cards_drawn = request.cookies.get('cards_drawn')
    if cards_drawn:
        cards_drawn=cards_drawn.split(",")
    else:
        cards_drawn=[]
    cards_drawn=[s for s in cards_drawn if len(s)>1]
    if not team_id:
        team_id=request.cookies.get('team_id')
    #plot_map([team_id])
    week_num=get_team_week_num(team_id)
    
    team_info=read_team_progress_at(team_id,week_num)
    team_info['team_id']=team_id
    login=request.cookies.get('login')
    city_names=read_cities_dic()[["Name","ID"]].values.tolist()#html_city_dic()
    #get commitment pledge
    player_leaderboard=get_players_progress(team_id=team_id)
    #get all cards to draw
    action_cards=read_action_cards()
    resp = make_response(render_template('teams.html',team_info=team_info,player_images=cards_drawn,login=login,player_leaderboard=player_leaderboard,city_names=city_names,parcitipant_data=parcitipant_data,action_cards=action_cards))
    resp.set_cookie('team_id',team_id)
    return resp


@app.route("/") #We then use the route() decorator to tell Flask what URL should trigger our function.
#go to the main page
@app.route('/main')
def main():
    team_leader_board=generate_team_leader_board()
    plot_all_map()
    for team_id in get_all_team_ids():
        plot_map([team_id])
    if 'login' in request.cookies:
        login=request.cookies.get('login')
    else:
        login='False'
    #plot_map()
    resp = make_response(render_template('main.html',login=login,team_leader_board=team_leader_board))


    resp.set_cookie('login',login)
    resp.set_cookie('id','all')
    resp.set_cookie('cards_drawn','')
    return resp
    
#log out
@app.route('/logout')
def logout():
    team_leader_board=generate_team_leader_board()
    login='False'
    player_leaderboard=[]
    resp = make_response(render_template('main.html',login=login,team_leader_board=team_leader_board,player_leaderboard=player_leaderboard))
    resp.set_cookie('login',login)
    resp.set_cookie('id','all')
    resp.set_cookie('cards_drawn','')
    return resp

#go the team page
@app.route('/teams', methods=['GET'])
def teams(team_id=[]):
    session.pop('_flashes', None)
    team_id=request.args.get('team_id')
    if if_team_exists(team_id):
        cards_drawn = request.cookies.get('cards_drawn')
        return team_webpage(cards_drawn,team_id)
    else:
        login=request.cookies.get('login')
        if login=="True":
            player_leaderboard=get_players_progress()
            resp = make_response(render_template('main.html',login=login,message="Error! The team id "+team_id+" does not exist!",player_leaderboard=player_leaderboard))
            return resp
        else:
            resp = make_response(render_template('main.html',login=login,message="Error! The team id "+team_id+" does not exist!"))
            return resp

#draw cards
@app.route("/Drawcards/", methods=['GET', 'POST'])
def get_img2():
    cards_drawn = request.cookies.get('cards_drawn')
    new_cards=draw_cards()
    while new_cards in cards_drawn:
            new_cards=draw_cards()
    cards_drawn+=","+new_cards

    resp=team_webpage(cards_drawn)
    resp.set_cookie('cards_drawn',cards_drawn)
    return resp
    #return  redirect(url_for('teams',player_images=result,player_image="cards_image/empty.jpg",rows=["1","2","3"]))

@app.route("/assign_plan_next_week/", methods=['GET', 'POST'])
def assign_plan():
    try:
        team_id=request.cookies.get('team_id')
        week_num=get_team_week_num(team_id)
        DriverId = str(request.form['DriverID'])
        if DriverId:
            user=get_user_info(DriverId)
            if DriverId in get_all_player_ids_in_team(team_id):
                modify_team_progress(team_id,week_num,"driver id",DriverId)
                flash("Driver ID # "+DriverId+"("+user["first_name"]+" "+user["last_name"]+") has been assigned as the Driver","driver_success")
            else:
                flash("Assignment failure! This driver is not in your team!","driver_error")
    except:
        flash("Assignment failure! Please check your input","driver_error")
    return team_webpage()



@app.route("/decide_destination_city/", methods=['GET', 'POST'])
def decide_destination_city():
    try:
        team_id=request.cookies.get('team_id')
        week_num=get_team_week_num(team_id)
        target_loc=str(request.form["destination"])
        if target_loc:
            modify_team_progress(team_id,week_num,"target location id",target_loc)
            flash("New destination has been assigned","driver_success")
        goal_miles=str(request.form["goal_miles"])
        bonus_miles=str(request.form["bonus_miles"])
        if goal_miles:
            if bonus_miles:
                goal_miles=int(goal_miles)+int(bonus_miles)
            modify_team_progress(team_id,week_num,"goal_miles",str(goal_miles))
            flash("Goal miles has been assigned","driver_success")    
    except:
        flash("Assignment_failure! Please check your input","driver_error")
    return team_webpage()

@app.route("/find_city_distance/", methods=['GET', 'POST'])
def print_city_distance():
    start_city=request.form["DropDownCity1"]
    end_city=request.form["DropDownCity2"]
    target_city=str(end_city)
    if len(start_city)>0 and  len(end_city)>0:
        if end_city<start_city:
            start_city,end_city=end_city,start_city
        message,category=find_customized_city_distance_between(start_city,end_city,target_city)
        flash(message,category)
    return team_webpage()

@app.route("/retrieve_participant_data/", methods=['GET', 'POST'])
def retrieve_participant_data():
    dataType=request.form["dataType"]
    player_id=str(request.form["id"])
    start,end=request.form["start_date"],request.form["end_date"]
    try: 
        user=get_user_info(player_id)
        user_name=user['first_name']+" "+user['last_name']
        name=player_id+"_"+dataType
        x,y=[],[]
        if not dataType:
            dataType='None'
        elif dataType=='steps':
            x,y=get_step_period(user,end_date=end,start_date=start)
            title="daily steps of "+user_name
        elif dataType=='calories':
            x,y=get_calories_period(user,end_date=end,start_date=start)
            title="daily calories of "+user_name
        elif dataType == 'Minutes Active' :
            x1,y=get_minutes_active_period(user,end_date=end,start_date=start,type="minutesLightlyActive")
            x2,y=get_minutes_active_period(user,end_date=end,start_date=start,type="minutesFairlyActive")
            x3,y=get_minutes_active_period(user,end_date=end,start_date=start,type="minutesVeryActive")
            title="daily "+dataType+" of "+user_name
            plot_minute_active(x1,x2,x3,y,name,title)
        elif dataType == 'weight':
            x,y=get_weight_period(user,end_date=end,start_date=start)
            title="daily weight of "+user_name+" (lbs)"
        elif dataType == 'bmi':
            x,y=get_bmi_period(user,end_date=end,start_date=start)
            title="daily bmi of "+user_name
        if x and dataType != 'minutes Active':
            plot_participant_data(x,y,name,title)
        return team_webpage(parcitipant_data=name)
    except:
        flash("Fail to find the participant data! Please check your user info file!","retrieval error!")
        return team_webpage()
@app.route("/update_miles/", methods=['GET', 'POST'])
def update_miles():
    player_id=str(request.form["id"])
    miles=request.form["miles"]
    user=get_user_info(player_id)
    current_team_id=None
    for team_id in get_all_team_ids():
        if player_id in get_all_player_ids_in_team(team_id): 
            current_team_id=team_id
            break
    if current_team_id:
        week_num=get_team_week_num(team_id)
        user_name=user['first_name']+" "+user['last_name']
        write_weekly_miles(player_id,miles,week_num)
        get_team_miles(team_id,week_num)
        flash("Successfully update the miles for player "+user_name+ "as "+miles+" at week #"+str(week_num),"update_miles")
    else:
        flash("Fail to find a team for player "+user_name,"update_miles_error")    
    return team_webpage()
@app.route("/React_with_cards/", methods=['GET', 'POST'])
def React_with_cards():
    team_id=request.cookies.get('team_id')
    week_num=get_team_week_num(team_id)
    team_info=read_team_progress_at(team_id,week_num)
    card_to_use=request.form['cardsUsed']
    if card_to_use and card_to_use in team_info["cards_at_hand"]:
        #delete this card from cards at hand
        team_info["cards_at_hand"].remove(card_to_use)
        modified_value=""
        for val in team_info["cards_at_hand"]:
            if val:
                modified_value+=val+";"
        modify_team_progress(team_id,week_num,"cards_at_hand",modified_value)
        
        #add this card to card used
        team_info["cards_used"]=team_info["cards_used"]+[card_to_use]
        modified_value=""
        for val in team_info["cards_used"]:
            if val:
                modified_value+=val+";"
        modify_team_progress(team_id,week_num,"cards_used",modified_value)
        flash("Successfully used the "+card_to_use+" card","defensive_card")
    else:
        flash("Fail to use the "+card_to_use+" card. Your team does not have it!","defensive_card_error")    
    return team_webpage()

@app.route("/attack_with_cards/", methods=['GET', 'POST'])
def attack_with_cards():
    team_id=request.cookies.get('team_id')
    week_num=get_team_week_num(team_id)
    team_info=read_team_progress_at(team_id,week_num)
    card_to_use=request.form['cardsUsed']
    target_team=request.form['target_team']
    if card_to_use and card_to_use in team_info["cards_at_hand"] and target_team in get_all_team_ids():
        #delete this card from your hand
        team_info["cards_at_hand"].remove(card_to_use)
        modified_value=""
        for val in team_info["cards_at_hand"]:
            if val:
                modified_value+=val+";"
        modify_team_progress(team_id,week_num,"cards_at_hand",modified_value)
        #add this card to cards used
        team_info["cards_used"]=team_info["cards_used"]+[card_to_use]
        modified_value=""
        for val in team_info["cards_used"]:
            if val:
                modified_value+=val+";"
        modify_team_progress(team_id,week_num,"cards_used",modified_value)
        #give this card to others
        target_week_num=get_team_week_num(target_team)
        target_team_info=read_team_progress_at(target_team,target_week_num)
        target_team_info["cards_received"]=target_team_info["cards_received"]+[card_to_use]
        modified_value=""
        for val in target_team_info["cards_received"]:
            if val:
                modified_value+=val+";"
        modify_team_progress(target_team,target_week_num,"cards_received",modified_value)
        flash("Successfully used the "+card_to_use+" card to team "+target_team,"offensive_card")
        
        
    else:
        flash("Fail to use the "+card_to_use+" card to team "+target_team+". Check if this team exists or if you have this card.","offensive_card_error")    
    return team_webpage()

@app.route("/assign_actual_miles/", methods=['GET', 'POST'])
def assign_actual_miles():
    try:
        team_id=request.cookies.get('team_id')
        week_num=get_team_week_num(team_id)
        team_info=read_team_progress_at(team_id,week_num)
        actual_miles=int(request.form['actual_miles'])+int(team_info["player_miles"])
        modify_team_progress(team_id,week_num,"actual_miles",str(actual_miles))
        flash("Successfully assign "+str(actual_miles)+" miles!","actual_miles")
    except:
        flash("Error, check your team csv file!","actual_miles_error")
    return team_webpage()

@app.route("/assign_points/", methods=['GET', 'POST'])
def assign_points():
    try:
        team_id=request.cookies.get('team_id')
        week_num=get_team_week_num(team_id)
        team_info=read_team_progress_at(team_id,week_num)
        points=int(request.form['points'])+int(team_info["points"])
        modify_team_progress(team_id,week_num,"points",str(points))
        flash("Successfully assign "+str(points)+" points","points")
    except:
        flash("Error, check your team csv file!","points_error")
    return team_webpage()
#start_new_week
@app.route("/start_new_week/", methods=['GET', 'POST'])
def start_new_week():
    try:
        team_id=request.cookies.get('team_id')
        week_num=get_team_week_num(team_id)
        new_week=str(int(week_num)+1)
        loction_id=str(request.form['start_new_week'])
        if loction_id:
            add_new_week_to_file(team_id,new_week,loction_id)
            plot_map([team_id])
            flash("Successfully start the new week. You are now at week "+new_week,"new_week")
        else:
            flash("Error, you cannot start the new week without a start location!","new_week_error")
    except:
        flash("Error, you cannot start the new week now!","new_week_error")
    return team_webpage()

@app.route("/store_card/", methods=['GET', 'POST'])
def store_card():
    card_name=request.form['store_card']
    if card_name:
        try:
            team_id=request.cookies.get('team_id')
            week_num=get_team_week_num(team_id)
            team_info=read_team_progress_at(team_id,week_num)
            team_info["cards_at_hand"]=team_info["cards_at_hand"]+[card_name]
            modified_value=""
            for val in team_info["cards_at_hand"]:
                    if val:
                        modified_value+=val+";"
            modify_team_progress(team_id,week_num,"cards_at_hand",modified_value)
            flash("Successfully add the "+card_name+" card","add_card")   
        except:
            flash("Failt to add the "+card_name+" card","add_card_error") 
    return team_webpage()


@app.route("/commitment_card/", methods=['GET', 'POST'])
def commitment_card():
    res={}
    f = request.form
    for key in f.keys():
        res[key]=str(request.form[key])
    if 'PlayerID' in res:
        team_id=request.cookies.get('team_id')
        week_num=str(get_team_week_num(team_id))
        plot_commitment_card(res,week_num)
    return team_webpage()
#
#login and redirect to the main page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.args.get('username')=='12' and request.args.get('password')=='123':
        message="Login success!"
        login='True'
        player_leaderboard=get_players_progress()
    else:
        message="Login failed! The username and password entered don't exist. Please try again!"
        login='False'
        player_leaderboard=[]
    team_leader_board=generate_team_leader_board()
    resp = make_response(render_template('main.html',login=login,message=message,player_leaderboard=player_leaderboard,team_leader_board=team_leader_board))
    resp.set_cookie('login',login)
    return resp

#open the login window
@app.route("/LoginWindow")
def LoginWindow():
    return render_template("login.html")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000) ## don't know why cannot connect to the phone
    