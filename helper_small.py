import requests
import json
from datetime import datetime
from datetime import timedelta
import random
import os
#Querying the user information
days_of_week=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
month=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
manually_input_dates=['baseline_start_dt','study_start_dt']
user_info_file="player/user info.csv"
def find_index_of_nth_letter_in_a_string(n,target_str,target_char=','):
    counter=0
    for i in range(len(target_str)):
        if target_str[i]==target_char:
            counter+=1
        if counter==n:
            return i
    return -1

def add_baseline_steps(baseline_steps,index_of_baseline,line):
    begining_index=find_index_of_nth_letter_in_a_string(index_of_baseline,line)
    ending_index=find_index_of_nth_letter_in_a_string(index_of_baseline+1,line)
    return line[:begining_index+1]+str(baseline_steps)+line[ending_index:]

def update_user_baseline(target_user_id,baseline_steps):
    update_needed=False
    with open("user info.csv") as f:
        lines=f.readlines()
        resulted_lines=[lines[0]]
        for line in lines[1:]:
            user_id_index=find_index_of_nth_letter_in_a_string(1,line)
            user_id=line[0:user_id_index]
            user_info=get_user_info(user_id=user_id,filename="user info.csv")
            if user_info['user_id']==str(target_user_id):
                if baseline_steps>0:
                    index_of_baseline=lines[0].index('baseline_steps_per_day')+1
                    index_of_baseline=lines[0][0:index_of_baseline].count(',')
                    line=add_baseline_steps(baseline_steps,index_of_baseline,line)
                    update_needed=True
            resulted_lines.append(line)
    if update_needed:
        with open("user info.csv","w") as f:
            for line in resulted_lines:
                f.write(line)
    return
def get_date_time(date=None):
    #transfer the date string to time format.
    #By default, return today
    if date is None:
        date=datetime.now()
    elif len(str(date))<=10:
        date=date_string_to_date(date)
        
    return date

def get_all_user_ids():
    #return the ids for all user
    user_ids=[]
    with open(user_info_file) as f:
        lines=f.readlines()[1:]
        for line in lines:
            if len(line)>3:
                user_ids.append(line.split(",")[0])
    return  user_ids

def get_user_info(user_id="1"):
    # return the user's information as a dictionary
    # maybe need to change filename, adding some directory
    user_id=str(user_id)
    user_info={}
    with open(user_info_file) as f:
        lines=f.readlines()
        variables=lines[0].replace("\n","")
        variables=variables.split(",")
        for line in lines:
            line=line.replace("\n","")
            words=line.split(",")
            if words[0]==user_id:
                for i in range(len(words)):
                    user_info[variables[i]]=words[i]
    if len(user_info.keys())==0:
        print("Error! the userid "+user_id+" does not contain information in the database!")
    for key in manually_input_dates:
        if len(user_info[key])==0:
            user_info[key]="2050-01-01"
    if len(user_info['report_day'])==0:
        user_info['report_day']=days_of_week[get_date_time(user_info['study_start_dt']).weekday()]
    #print(user_info)
    return user_info

def get_step_period(user,previous_days=31,end_date=None,start_date=None):
    #[1]	This function returns the dates and user steps from the end date, including the previous days. By default, it includes 31 days.
    #by default, today is the enddate. You can input a new end date with the format YYYY-MM-DD
    
    activities_header={'Authorization':'Bearer {}'.format(user['permanent_token'])}
    end_date=get_date_time(end_date)
    today=str(end_date)[0:10]
    if start_date is None:
        start_date=str(end_date-timedelta(days = previous_days-1))[0:10]
        previous_days=num_days_between(end_date,start_date)
    else:
        start_date=str(get_date_time(start_date))[0:10]
        
    activities=requests.get('https://api.fitbit.com/1/user/-/activities/tracker/steps/date/'+start_date+'/'+today+'.json',headers=activities_header).json()
    if  'activities-tracker-steps' in activities.keys():
        activities=activities['activities-tracker-steps']
        steps,x_values=[],[]
        for i in range(len(activities)):
            steps.append(int(activities[i]['value']))
            x_values.append(activities[i]['dateTime'])
        return x_values,steps
    else:
        print(activities)
    return
def get_calories_period(user,end_date,start_date):
    activities_header={'Authorization':'Bearer {}'.format(user['permanent_token'])}
    end_date=get_date_time(end_date)
    today=str(end_date)[0:10]
    start_date=str(get_date_time(start_date))[0:10]
    activities=requests.get('https://api.fitbit.com/1/user/-/activities/tracker/calories/date/'+start_date+'/'+today+'.json',headers=activities_header).json()
    if  'activities-tracker-calories' in activities.keys():
        activities=activities['activities-tracker-calories']
        steps,x_values=[],[]
        for i in range(len(activities)):
            steps.append(float(activities[i]['value']))
            x_values.append(activities[i]['dateTime'])
    return  x_values,steps
def get_minutes_active_period(user,end_date,start_date,type):#minutesLightlyActive, minutesFairlyActive, minutesVeryActive
    activities_header={'Authorization':'Bearer {}'.format(user['permanent_token'])}
    end_date=get_date_time(end_date)
    today=str(end_date)[0:10]
    start_date=str(get_date_time(start_date))[0:10]
    activities=requests.get('https://api.fitbit.com/1/user/-/activities/tracker/'+type+'/date/'+start_date+'/'+today+'.json',headers=activities_header).json()
    if  'activities-tracker-'+type in activities.keys():
        activities=activities['activities-tracker-'+type]
        steps,x_values=[],[]
        for i in range(len(activities)):
            steps.append(float(activities[i]['value']))
            x_values.append(activities[i]['dateTime'])
    return  x_values,steps
def get_weight_period(user,end_date,start_date):
    activities_header={'Authorization':'Bearer {}'.format(user['permanent_token'])}
    end_date=get_date_time(end_date)
    today=str(end_date)[0:10]
    start_date=str(get_date_time(start_date))[0:10]
    activities=requests.get('https://api.fitbit.com/1/user/-/body/weight/date/'+start_date+'/'+today+'.json',headers=activities_header).json()
    if  'body-weight' in activities.keys():
        activities=activities['body-weight']
        steps,x_values=[],[]
        for i in range(len(activities)):
            steps.append(float(activities[i]['value'])*2.20462)
            x_values.append(activities[i]['dateTime'])
    return  x_values,steps
def get_bmi_period(user,end_date,start_date):
    activities_header={'Authorization':'Bearer {}'.format(user['permanent_token'])}
    end_date=get_date_time(end_date)
    today=str(end_date)[0:10]
    start_date=str(get_date_time(start_date))[0:10]
    activities=requests.get('https://api.fitbit.com/1/user/-/body/bmi/date/'+start_date+'/'+today+'.json',headers=activities_header).json()
    #print(activities)
    if  'body-bmi' in activities.keys():
        activities=activities['body-bmi']
        steps,x_values=[],[]
        for i in range(len(activities)):
            steps.append(float(activities[i]['value']))
            x_values.append(activities[i]['dateTime'])
    return  x_values,steps
def date_string_to_date(date):
    #change the string date to date format
    #sample input "YYYY-MM-DD" or "YYYY/MM/DD" 
    date=str(date)[0:10]
    if "-" in date:
        date=date.split("-")
    elif "/" in date:
        date=date.split("/")
    #print(date)
    if len(date[0])==4:
        return datetime(int(date[0]), int(date[1]), int(date[2]))
    elif len(date[2])==4:
        if not date[0].isdigit():
            date[0]=month.index(date[0])+1

        return datetime(int(date[2]), int(date[0]), int(date[1]))
def num_days_between(d1, d2):
    #find out the number of days between two dates 
    if 'datetime.datetime' not in str(type(d1)):
        d1=date_string_to_date(d1)
    if 'datetime.datetime'not in str(type(d2)):
        d2=date_string_to_date(d2)
    return abs((d2.date() - d1.date()).days)

def is_report_day(user,date):
    #find out if this date is the report day of the user
    target_date=date_string_to_date(date).weekday()
    
    return days_of_week[target_date]==user['report_day']
def number_of_days_to_report_day(user,date):
    index_target=date_string_to_date(date).weekday()
    index_report=days_of_week.index(user['report_day'])
    num_days=index_report-index_target
    if num_days<0:
        num_days+=7
    return num_days
def is_one_day_before_report_day(user,date):
    #find out if this date is the report day of the user
    #sample input date "YYYY-MM-DD" or "YYYY/MM/DD" 
    target_date=date_string_to_date(date).weekday()
    if target_date==6:
        target_date=0
    else:
        target_date=int(target_date+1)
    #print("today is:"+days_of_week[date_string_to_date("2022-01-29").weekday()])
    if days_of_week[target_date]==user["report_day"]:
        return True
    #
    return False
def get_daily_step(user,date):
    #get the daily step of the user at a particular date
    activities_header={'Authorization':'Bearer {}'.format(user['permanent_token'])}
    activities=requests.get('https://api.fitbit.com/1/user/-/activities/date/'+date+'.json',headers=activities_header).json()
    #print(activities)
    if "summary" in activities.keys():
        steps=activities['summary']['steps']
    else:
        steps=0
    return steps

def get_step_goal(user,date):
    #get the daily step goal of the user at a particular date
    activities_header={'Authorization':'Bearer {}'.format(user['permanent_token'])}
    activities=requests.get('https://api.fitbit.com/1/user/-/activities/date/'+date+'.json',headers=activities_header).json()
    steps=0
    if 'goals' in activities.keys():
        steps=activities['goals']['steps']
    while (('goals' not in activities.keys() or steps<1) and date>=user["study_start_dt"]):
        date=date_string_to_date(date)
        date = date - timedelta(days = 1)
        date=str(date)[0:10]
        activities=requests.get('https://api.fitbit.com/1/user/-/activities/date/'+date+'.json',headers=activities_header).json()
        if 'goals' in activities.keys():
            steps=activities['goals']['steps']
    return steps

def update_step_goal(user,update_value):
    # update the user step goal
    # you can only update the step goal for the current date
    activities_header={'Authorization':'Bearer {}'.format(user['permanent_token'])}
    parameters={'peroid':'daily','type':"steps",'value':str(update_value)}
    requests.post('https://api.fitbit.com/1/user/-/activities/goals/daily.json',params=parameters,headers=activities_header)
    return

def find_baseline_count(user):
    # find out the baseline step count of an user
    # this function returns the average daily steps since the baseline start date to today
    # at least 7 days is needed for to calculate the baseline average.
    today=get_date_time()
    yesterday=today-timedelta(days=1)

    baseline_start_dt=date_string_to_date(user['baseline_start_dt'])
    valid_step_start_dt=baseline_start_dt+timedelta(days=7)
    step_end_date=valid_step_start_dt+timedelta(days=7)
    step_end_date_extended=step_end_date+timedelta(days=7)
    baseline,extended_baseline=0,0

    if yesterday>step_end_date_extended:
        baseline_time,baseline_count=0,0
        steps=get_step_period(user,start_date=valid_step_start_dt,end_date=step_end_date_extended,previous_days=14)
        for step in steps[1]:
            current_step=int(step)
            if current_step >1000:
                baseline_count+=current_step
                baseline_time+=1
        if baseline_time>=4:
            extended_baseline=baseline_count/baseline_time
    if yesterday>step_end_date:
        baseline_time,baseline_count=0,0
        steps=get_step_period(user,start_date=valid_step_start_dt,end_date=step_end_date,previous_days=7)
        for step in steps[1]:
            current_step=int(step)
            if current_step >1000:
                baseline_count+=current_step
                baseline_time+=1
        if baseline_time>=4:
            baseline=baseline_count/baseline_time
    return [int(baseline),int(extended_baseline)]

#write query functions
def AvgSteps_per_day(user,end_date):
    #calculate the weekly average step count of the user ending at particular end date
    total_steps=0
    current_date=date_string_to_date(end_date)
    step_count=0
    for i in range(7):
       past_date = current_date - timedelta(days = i)
       past_date=str(past_date)[0:10]
       temp_step=get_daily_step(user,past_date)
       if temp_step>0:
        step_count+=1
        total_steps+=temp_step
       #print(get_daily_step(user,past_date))
    if step_count>0:
        return int(total_steps/step_count)
    else:
        return 0

def find_new_step_goal(user,current_goal):
    # find out the new step goal for the user
    if int(user["baseline_steps_per_day"])<5000:
        return min(int(current_goal*1.15),7000)
    else:
        return min(int(current_goal*1.15),10000)

def update_goal(user,today=None):
    #update the step goal
    today=get_date_time()
    yesterday=today- timedelta(days = 1)
    if is_report_day(user,today):
        current_goal=get_step_goal(user,str(today)[0:10])
        yesterday_goal=get_step_goal(user,str(yesterday)[0:10])
        if current_goal<=yesterday_goal:
            #update the goal if it has not been upated (namely, different from the one in the yesterday)
            update_value=find_new_step_goal(user,current_goal)
            update_step_goal(user,update_value)
    return

def count_0_date(user,end_date=None):
    #find the number of consequtive invalid (0-step) date from end_date, by default, the end_date is yesterday
    end_date=get_date_time(end_date)
    _,steps=get_step_period(user,previous_days=10,end_date=str(end_date)[0:10])
    count=0
    steps=[int(i) for i in steps]
    index=len(steps)-1
    temp_step=steps[index]
    while(temp_step<1 and index>1):
        count+=1
        index=index-1
        temp_step=steps[index]
    return count

def check_synced(user,date=None):
    #check if the device has been synced for the user
    date=get_date_time(date)
    activities_header={'Authorization':'Bearer {}'.format(user['permanent_token'])}
    devices=requests.get('https://api.fitbit.com/1/user/-/devices.json',headers=activities_header).json()
    #print(devices)
    for device in devices:
        #print(device)
        if 'Inspire' in device['deviceVersion'] or 'MobileTrack' in device['deviceVersion']:
            synced_time=date_string_to_date(device['lastSyncTime'][0:10])
            print("user "+user['user_id']+"'s device last synced at: "+str(synced_time))
            if synced_time>date:
                return True
    if len(devices)==0:
        return True
    return False

def last_synced_at(user):
    #check if the device has been synced for the user
    activities_header={'Authorization':'Bearer {}'.format(user['permanent_token'])}
    devices=requests.get('https://api.fitbit.com/1/user/-/devices.json',headers=activities_header).json()
    #print(devices)
    for device in devices:
        #print(device)
        if 'Inspire' in device['deviceVersion'] or 'MobileTrack' in device['deviceVersion']:
            print("user "+user['user_id']+"'s device last synced at: "+device['lastSyncTime'])
            synced_time=date_string_to_date(device['lastSyncTime'][0:10])
            return synced_time
    return None

def low_battery_level(user):
    #check if the user's battery is low.
    activities_header={'Authorization':'Bearer {}'.format(user['permanent_token'])}
    devices=requests.get('https://api.fitbit.com/1/user/-/devices.json',headers=activities_header).json()
    #print(devices)
    for device in devices:
        if 'Inspire' in device['deviceVersion']:
            battery=int(device['batteryLevel'])
            print("user "+user['user_id']+"'s battery level: "+str(battery))
            if battery<15:
                return True
    return False

def write_error(user_id,date,error_type="message",reason=""):
    # record the errors to the error_log.csv file.
    with open("error_log.csv", "a") as f:
        f.write(str(date)[0:10]+","+user_id+","+error_type+","+reason+"\n")
    print("Error recorded at "+str(date)[0:10]+", for user "+user_id+", in "+error_type+". Error source: "+reason+"\n")
    return False

def get_gmail_users():
    # return the list of user ids to whom the text message is sent by gmail
    gmail_list=[]
    ids=get_all_user_ids()
    for id in ids:
        user_info=get_user_info(id)
        if "republicwireless" in user_info["alternative_email"] or "republicwireless" in user_info["email"]:
            gmail_list.append(id)
    return gmail_list

#today=str(datetime.now())[0:10]
#AvgSteps_per_day(user,"2021-09-15")
#find_baseline_count(user)

#is_report_day(user,"2021-09-14")

#a=get_step_goal(user,"2021-09-17")
#update_step_goal(user,10000)
#b=get_step_goal(user,"2021-09-17")
#print(a)
#print(b)\

#find_baseline_count(user)
#update_user_baseline("1",8988)
#date=get_date_time()
#x=number_of_days_to_report_day(user,date)
#x,y=get_step_period(user,previous_days=31,end_date=None)
#print(x)
#print(y)
#z=count_0_date(user,end_date=None)
#print(z)
'''
user=get_user_info("1")
print(get_bmi_period(user,"2022-08-10","2022-08-20"))
'''
