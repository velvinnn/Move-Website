import matplotlib.pyplot as plt

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
