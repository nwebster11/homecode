import wx
import csv
import OtherUtils as otherUtils

class Mg:
    def __init__(self,mgName,order):
        self.name = mgName
        self.order = order

class Exercise:
    def __init__(self,exerName):
        self.name = exerName
        self.mgs = {}
        self.wt = None
        self.delta = None
    def rank(self):
        # return the minimum of the mg rank
        ranks = []
        for mg in self.mgs.values():
            ranks.append(mg.order)
        return min(ranks)

class Gym:
    def __init__(self):
        #self.basepath = "C:/Dropbox/Projects/Gym Weights/"
        self.basepath = "C:/Users/nwebster/Dropbox/Projects/Gym Weights/"
        #self.basepath = "/Users/nathan/Dropbox/Projects/Gym Weights/"
        self.exers = {}
        self.mgs = {}
        self.userdata = {}
        self.workout = []
        self.prefs = {}
        # read gym mg data
        df = otherUtils.DataFrame.read_csv(self.basepath + "gymMgData.csv")
        for row in df.rows:
            mgName = row["Muscle group"]
            order = int(row["Order"])
            self.mgs[mgName] = Mg(mgName,order)
        # read gym exercise data
        infile = open(self.basepath + "gymExerciseData.csv",'rb')
        lines = infile.readlines()
        header = lines.pop(0)
        for line in lines:
            line = line.rstrip()
            tokens = line.split(",")
            exerName = tokens.pop(0)
            exer = Exercise(exerName)
            for token in tokens:
                if token != "":
                    mgName = token
                    exer.mgs[mgName] = self.mgs[mgName]
            self.exers[exerName] = exer
        # read user data
        infile = open(self.basepath + "userData.csv",'rb')
        reader = csv.reader(infile)
        header = next(reader)
        for row in reader:
            exer = self.exers[row[0]]
            exer.wt = int(row[1])
            exer.delta = row[2]
            self.userdata[exer.name]=exer
        infile.close()
        # read prevWorkout
        infile = open(self.basepath + "workout.csv",'rb')
        reader = csv.reader(infile)
        header = next(reader)
        for row in reader:
            exer = Exercise(row[0])
            self.workout.append(exer)
            # no need to read the wt and delta, because it is already stored in userdata
        infile.close()
        # read exercise prefs
        infile = open(self.basepath + "exerPrefs.csv",'rb')
        reader = csv.reader(infile)
        header = next(reader)
        for row in reader:
            exerName = row[0]
            pref = int(row[1])
            self.prefs[exerName] = pref
        infile.close()
    def update_user_data(self):
        print "updating user data"
        for exer in self.workout:
            self.userdata[exer.name].wt = exer.wt
            self.userdata[exer.name].delta = exer.delta
        # write userdata to file
        outfile = open(self.basepath + "userData.csv",'wb')
        writer = csv.writer(outfile)
        writer.writerow(["name","weight","delta"])
        for exerName in sorted(self.userdata.keys()):
            exer = self.userdata[exerName]
            writer.writerow([exerName,exer.wt,exer.delta])
        outfile.close()        
    def generate_new_workout(self,writeWorkout=True):
        print "generating new workout"
        from random import shuffle
        self.workout = []
        self.coveredMgs = set()
        exersToTry = list(self.exers)
        shuffle(exersToTry)
        for exerName in sorted(self.prefs.keys()):
            prefValue = self.prefs[exerName]
            position = exersToTry.index(exerName)
            # determining queue jump length based on pref value
            n = len(exersToTry)
            if (prefValue == -1):
                jump = int(n/2.0)
            if (prefValue == -2):
                jump = (int)(n/3.0)
            if (prefValue == -3):
                jump = (int)(n/4.0)
            if (prefValue == 1):
                jump = -(int)(n/2.0)
            if (prefValue == 2):
                jump = -(int)(n/3.0)                
            if (prefValue == 3):
                jump = -(int)(n/4.0)
            # move the item in the queue
            exerName = exersToTry.pop(position)
            newPos = position + jump
            newPos = min(newPos,n-1)
            newPos = max(newPos,0)
            exersToTry.insert(newPos,exerName)
        for exerName in exersToTry:
            exer = self.exers[exerName]
            commonMgs = set(exer.mgs.keys()).intersection(self.coveredMgs)
            if len(commonMgs) == 0: # verify that  it is not duplicating coverage
                # if it is not duplicating coverage, then it must be covering new muscle groups!
                # no need for further comparisons
                self.workout.append(exer)
                    # ! add the exercise as listed in the userdata, because this is where it tells the wt,delta
                self.coveredMgs = self.coveredMgs.union(set(exer.mgs.keys()))
                if len(self.coveredMgs) == len(self.mgs.keys()):
                    break
        # sort the workout exercises by Mg order
        ## this is the biggest uncertainty. could ask Jorg for help
        print "finished picking workout exercises"
        print ""
        self.workout.sort(key = lambda x: x.rank())
        # write newly generated workout to file
        if writeWorkout:
            outfile = open(self.basepath + "workout.csv",'wb')
            writer = csv.writer(outfile)
            writer.writerow(["name","weight","delta"])
            for exer in self.workout:
                writer.writerow([exer.name,exer.wt,exer.delta])
            outfile.close()
    def print_workout_to_console(self):
        print "new workout:"
        print "exerName\twt\tdelta"
        for exer in self.workout:
            print exer.name,"\t",str(exer.wt),"\t",exer.delta

class GymGui(wx.Frame):
    def __init__(self,parent,id):
        wx.Frame.__init__(self,parent,id,"Gym GUI",size=(600,700),pos=(20,20))
        self.panel = wx.Panel(self)
        self.topText = wx.StaticText(self.panel, label="Complete the workout data", pos=(200, 10))
        self.weightsTableTitle = wx.StaticText(self.panel,label="Weights Table",pos=(200,80))
        y = 100
        self.headings = []
        self.labels = []
        self.wtFields = []
        self.deltaFields = []
        header = ["name","wt","delta","wt","delta"]
        startcol = [10,310,380,430,500]
        k = 5
        for i in range(k):
            self.headings.append(wx.StaticText(self.panel,label=header[i],pos=(startcol[i],y)))
        self.gym = Gym()
        for exer in self.gym.workout:
            y += 30
            self.labels.append(wx.StaticText(self.panel,label=exer.name,pos=(startcol[0],y)))
            userExer = self.gym.userdata[exer.name]
            # check again if the above line is necessary
            #  i think now I have the wt and delta already in there
            self.labels.append(wx.StaticText(self.panel,label=str(userExer.wt),pos=(startcol[1],y)))
            self.labels.append(wx.StaticText(self.panel,label=userExer.delta,pos=(startcol[2],y)))
            self.wtFields.append(wx.TextCtrl(self.panel,value=str(userExer.wt),pos=(startcol[3],y),size=(60,25)))
            self.deltaFields.append(wx.TextCtrl(self.panel,value=userExer.delta,pos=(startcol[4],y),size=(60,25)))
        updateButton = wx.Button(self.panel,label="Update",pos=(200,y+30))
        self.Bind(wx.EVT_BUTTON,self.update,updateButton)
        self.Bind(wx.EVT_CLOSE,self.closewindow)
        self.Show()
    def update(self,event):
        print "update button pressed"
        i = -1
        for exer in self.gym.workout:
            i += 1            
            exer.wt = int(self.wtFields[i].GetValue())
            exer.delta = self.deltaFields[i].GetValue()
        self.gym.update_user_data()        
        self.gym.generate_new_workout()
        self.gym.print_workout_to_console()
        # I couldn't change the state of the elements in the 
        #  wxPython Frame after updating, so I'm just going to 
        # write the results to the console.
        # A nice variant of this would be to make it html
        #  and refer the user to the html page
        self.Destroy()
    def closewindow(self,event):
        self.Destroy()

def runGym():
    app=wx.App(False)
    GymGui(parent=None,id=-1)
    app.MainLoop()
runGym()

def test_exer_freqs():
    # randomly generate 1000 workouts
    # for each mg, list the exers and their freq
    t = otherUtils.Tally()
    g = Gym()
    gymMgs = set(g.mgs)
    for i in range(10000):
        g.generate_new_workout(writeWorkout=False)
        missingMgs = gymMgs.difference(g.coveredMgs)
        mmgsStr = ",".join(sorted(list(missingMgs)))
        t.add(mmgsStr)
    t.showAll()
#test_exer_freqs()
        
