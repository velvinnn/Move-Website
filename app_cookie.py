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
    resp = make_response(render_template('teams.html',team_info=team_info,player_images=get_cards_list(cards_drawn),login=login,player_leaderboard=player_leaderboard,city_names=city_names,parcitipant_data=parcitipant_data))
    resp.set_cookie('team_id',team_id)
    return resp


@app.route("/") #We then use the route() decorator to tell Flask what URL should trigger our function.
#go to the main page
@app.route('/main')
def main():
    plot_map()
    for t_id in get_all_team_ids():
        week_num=get_team_week_num(t_id)
        update_team_at_week(t_id,week_num)
        plot_map([t_id])
    team_leader_board=generate_team_leader_board()
    if 'login' in request.cookies:
        login=request.cookies.get('login')
    else:
        login='False'
    if login == 'True':
        player_leaderboard=get_players_progress()
    else:
        player_leaderboard=[]
    resp = make_response(render_template('main.html',login=login,team_leader_board=team_leader_board,player_leaderboard=player_leaderboard))

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
    new_cards='cards_image/'+draw_cards()
    while new_cards in cards_drawn:
            new_cards='cards_image/'+draw_cards()
    cards_drawn+=","+new_cards

    resp=team_webpage(cards_drawn)
    resp.set_cookie('cards_drawn',cards_drawn)
    return resp
    #return  redirect(url_for('teams',player_images=result,player_image="cards_image/empty.jpg",rows=["1","2","3"]))


@app.route("/assign_plan_next_week/", methods=['GET', 'POST'])
def assign_plan():
    WeekNum=request.form['WeekNum']
    if len(WeekNum)==0:
        flash("Please enter a week number!","error")
    else:
        WeekNum=int(WeekNum)
        team_id=request.cookies.get('team_id')
        week_num=get_team_week_num(team_id)
        #input week num
        if WeekNum>week_num:
            flash("Your target week is Week "+str(WeekNum),"success")
            #change driver:
            DriverId = request.form['DriverID']
            
            if len(DriverId)>0:
                if DriverId in get_all_player_ids_in_team(team_id):
                    modify_team_progress(team_id,WeekNum,"driver id",DriverId)
                    update_player_cards(DriverId,"1",WeekNum)
                    user=get_user_info(DriverId)
                    flash("Driver ID # "+DriverId+"("+user["first_name"]+" "+user["last_name"]+") has been assigned as the Driver","success")
                else:
                    flash("Driver ID "+DriverId+" is not in your team!","error")
            
            #assign destination city
            CityID = request.form['CityID']
            if len(CityID)>0:
                states,cities,lat,long,cids,points=read_cities_dic()
                if CityID in cids:
                    c_index=cids.index(CityID)
                    modify_team_progress(team_id,WeekNum,"target location id",CityID)
                    flash("City ID # "+CityID+"("+cities[c_index]+", "+states[c_index]+") has been assigned as the destination.","success")
                else:
                    flash("City ID "+CityID+" does not exist!","error")
        
            # assign card to player
            for i in range(1,10):
                CardID=request.form['CardName'+str(i)]
                PlayerID=request.form['PlayerName'+str(i)]
                if len(CardID)>0 and len(PlayerID)>0:
                    if not (CardID in get_all_cards_ids()):
                        flash("CardID "+str(CardID)+" does not exist!","error")
                    elif not (PlayerID in get_all_player_ids_in_team(team_id)):
                        flash("PlayerID "+str(PlayerID)+" is not in the team!","error")
                    else:
                        update_player_cards(PlayerID,CardID,WeekNum)
                        user=get_user_info(PlayerID)
                        flash("Card # "+str(CardID)+" successfully assigned to Player # "+str(PlayerID)+"("+user["first_name"]+" "+user["last_name"]+")!","success")
        else:
            flash("You input Week "+str(WeekNum)+" is less than the current week ( Week "+str(week_num)+")","error")
    return team_webpage()

@app.route("/assign_commitment_pledge_next_week/", methods=['GET', 'POST'])
def assign_cp():
    WeekNum=request.form['WeekNum']
    if len(WeekNum)==0:
        flash("Please enter a week number!","pc_error")
    else:
        WeekNum=int(WeekNum)
        team_id=request.cookies.get('team_id')
        week_num=get_team_week_num(team_id)
        #input week num
        if WeekNum>week_num:
            flash("Your target week is Week "+str(WeekNum),"pc_success")
            #change driver:
            PlayerId = request.form['PlayerID']
            
            if not (PlayerId  in get_all_player_ids_in_team(team_id)):
                flash("PlayerID "+str(PlayerId )+" is not in the team!","pc_error")
            else:

                if request.form.get('Driver bonus'):
                    update_player_cards(str(PlayerId),"1",WeekNum)
                if request.form.get("Try something new bonus"):
                    update_player_cards(str(PlayerId),"2",WeekNum)
                    with open("player/report/player#"+str(PlayerId)+"_week"+str(WeekNum)+".txt","a") as f:
                        f.write("Try something new bonus: "+request.form.get('Something new string')+"\n")
                if request.form.get("Double-up bonus"):
                    update_player_cards(str(PlayerId),"3",WeekNum)
                    if len(request.form.get('DoublePlayerID1')) >0 or len(request.form.get('DoublePlayerID2')) >0:
                        with open("player/report/player#"+str(PlayerId)+"_week"+str(WeekNum)+".txt","a") as f:
                            if len(request.form.get('DoublePlayerID1')) >0:
                                f.write("Double-up bonus Player: "+request.form.get('DoublePlayerID1')+"\n")
                            if len(request.form.get('DoublePlayerID2')) >0:
                                f.write("Double-up bonus Player: "+request.form.get('DoublePlayerID2')+"\n")
                flash("Commitment pledge created for Player #"+str(PlayerId)+"! Remember that you also need to assign the challenge card to the player.","pc_success")
                
            '''
            if not(request.form.get("Driver bonus")is None):
                 flash("Driver bonus assigned","pc_success")   
            '''
        else:
            flash("Your have completed week #"+str(week_num)+", you cannot input week prior to that","pc_error")
    return team_webpage()

@app.route("/find_city_distance/", methods=['GET', 'POST'])
def print_city_distance():
    start_city=request.form["DropDownCity1"]
    end_city=request.form["DropDownCity2"]
    if len(start_city)>0 and  len(end_city)>0:
        if end_city<start_city:
            start_city,end_city=end_city,start_city
        
        message,category=find_customized_city_distance_between(start_city,end_city)
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
        flash("Successfully update the miles for player "+user_name+ "as "+miles+" at week #"+str(week_num),"update_miles")
    else:
        flash("Fail to find a team for player "+user_name,"update_miles_error")    
    return team_webpage()

@app.route("/assign_challenge_to_commitment/", methods=['GET', 'POST'])
def assigne_challenge():
    card_id=request.form['CardID']
    card_info=read_card_info(card_id)
    success=False
    if "card type" in card_info.keys():
        if card_info["card type"] =='Chanllenge':
            success=True
            
            flash("A commitment Pledge has been created from card #"+card_id,"challenge_success")
            return team_webpage(card_challenge_id=card_id)
    if not success:
        flash("Card #"+card_id+" is not a challenge card! Please assign a new one!","challenge_error")
    
    return team_webpage()

@app.route("/send_email/", methods=['GET', 'POST'])
def send_email():
    email=request.form['email']
    message=request.form['message']
    if len(message)>0 and len(email)>0:
        try:
            '''
            email_message = MIMEMultipart()
            body_part = MIMEText(message, 'plain')
            email_message.attach(body_part)
            #email_message.add_attachment(open(filename, "r").read(), filename=filename)
            email_message["Subject"] = "Message from Gamification website"
            email_message["From"] = outlook_sender_email
            email_message["To"] = email
            port = 587  # For SSL
            with smtplib.SMTP('smtp-mail.outlook.com', port) as server:
                server.starttls()
                server.login(outlook_sender_email, password)
                server.sendmail(outlook_sender_email, email,email_message.as_string()) #.as_string())
                flash("message sent","email_success")
            '''
            port = 465  # For SSL
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                server.login(gmail_sender_email, password)
                server.sendmail(gmail_sender_email, email,"From Gamification website: "+message)
                flash("message sent","email_success")
        except:
            flash("message failure. Check email address","email_error")
    else:
        flash("Please enter complete information","email_error")
    return team_webpage()


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
    