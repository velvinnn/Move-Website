import matplotlib.pyplot as plt
import json
def plot_participant_data(x,y,name,title):
    plt.figure()
    plt.plot(x,y)
    plt.title(title)
    plt.xticks(rotation = 75)
    plt.tight_layout()
    plt.savefig("static/participant_data/"+name)
    return

def plot_minute_active(x1,x2,x3,y,name,title):
    plt.figure()
    plt.plot(x1,y,label="minutes Lightly Active") #["minutesLightlyActive", "minutesFairlyActive", "minutesVeryActive"]
    plt.plot(x2,y,label="minutes Fairly Active")
    plt.plot(x3,y,label="minutes Very Active")
    plt.legend(loc="upper left")
    plt.title(title)
    plt.xticks(rotation = 75)
    plt.tight_layout()
    plt.savefig("static/participant_data/"+name)
    return

def plot_commitment_card(res,week_num):
    
    res["My challenge this week is to:"] = res.pop("challenge", "")
    res["If I do this I will earn ___ miles for the team:"] = res.pop("base_miles", "")
    res["In addition, I agree to collaborate with player #:"] = res.pop("collaboratorID", "")
    res["and I will:"] = res.pop("collaboration_challenge", None)
    res["I will document the completion of my challenge by:"] = res.pop("Way2DocumentChallenge", "")
    res["Bonus miles if I collaborate with a teammate:"] = res.pop("bonusMiles", "")
    res["Total miles if I honor my commitment and collaborate:"] = res.pop("totalMiles", "")
    res["Date of filling the commmitment card:"] = res.pop("FillDate", "")
    res["Expected date of completing the commmitment card:"] = res.pop("CompletionDate", "")
    ''''''
    with open('static/commitment_cards/'+res['PlayerID']+'_week'+week_num+'.json', 'w+') as fp:
        json.dump(res, fp,indent=4)
    return
