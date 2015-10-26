import matplotlib.pyplot as plot
import numpy as np
import csv
from xml.dom import minidom
import sys
import urllib
import copy

# this is a working copy of IterisReid.Utils.py
#  I haven't figured out how to refer directly to it or deal with dependency issue,
#  so this is a workaround


class Distribution:
    def __init__(self,values):
        self.x = values
    def plotHistogram(self,xLabel,title = "Histogram",nBins = 40,valRange=None,destination="Screen",outfileName=None):
        plot.hist(self.x,bins=nBins,range=valRange)
        plot.title(title)
        plot.xlabel(xLabel)
        plot.ylabel("Frequency")
        if destination=="Screen":
            plot.show()
        else:
            plot.savefig(outfileName)
            print "figure printed to",outfileName
        plot.clf()
    def print_descStatsNumpy(self): 
        mean = np.mean(self.x) 
        median = np.median(self.x) 
        sd = np.std(self.x) 
        minVal = np.min(self.x) 
        maxVal = np.max(self.x) 
        n = len(self.x) 
        print "n =",n 
        print "min =",minVal 
        print "max =",maxVal 
        print "mean =",mean 
        print "median =",median 
        print "stdev =",sd

class StatMeasure:
    def __init__(self):
        self.statMeasures = {}
    def setStatMeasure(self,name,value):
        self.statMeasures[name]=value

class DescStats:
    def __init__(self,x):
        self.m = {}
        self.statNames = []        
        self.m["n"] = len(x)
        self.statNames.append("n")
        if self.m["n"] == 0:
            self.m["minVal"] = "None"
            self.statNames.append("minVal")
            self.m["maxVal"] = "None"
            self.statNames.append("maxVal")
            self.m["mean"] = "None" 
            self.statNames.append("mean")
            self.m["median"] = "None"
            self.statNames.append("median")
            self.m["sd"] = "None" 
            self.statNames.append("sd")
        else:
            self.m["minVal"] = np.min(x) 
            self.statNames.append("minVal")
            self.m["maxVal"] = np.max(x) 
            self.statNames.append("maxVal")
            self.m["mean"]= np.mean(x) 
            self.statNames.append("mean")
            self.m["median"] = np.median(x) 
            self.statNames.append("median")
            self.m["sd"] = np.std(x) 
            self.statNames.append("sd")
    def getStat(self,statName):
        return self.m[statName]
    @staticmethod
    def statMeasuresList():
        return ["n","minVal","maxVal","mean","median","sd"]
    def allStats(self):
        for stat in self.statMeasuresList():
            print stat,"=",self.getStat(stat)
                                      
class FileUtils:
    def dirList(self,path):
        import os
        fileList = []
        for dirname,dirnames,filenames in os.walk(path):
            for filename in filenames:
                entry = os.path.join(dirname,filename)
                fileList.append(entry)
        return fileList

def rowCellCountDistr(self,infileName):
    print "Row cell count distribution for",infileName,":"
    infile = open(infileName,'rb')
    freq = {}
    reader = csv.reader(infile)
    rowCount = 0
    for row in reader:
        if rowCount % 1000000 == 0:
            print "row",rowCount,"is",row
        if rowCount == 0:
            nFields = len(row)
        else: 
            nCells = len(row)
            if nCells < nFields:
                print "nCells=",nCells,"in row",rowCount
            if freq.has_key(nCells):
                thisFreq = freq[nCells]
                thisFreq += 1
                freq[nCells] = thisFreq
            else:
                freq[nCells] = 1
        rowCount += 1
    print freq
    print "data row count=",rowCount-1

# if the number of row entries are less than 
#  the number of entries in the header, 
#  this method will add extra
#  blank "" entries to any rows with fewer entries
#  than the number of elements in the header row
def padRowTrailingFields(self,infileName,outfileName):
    infile=open(infileName,'rb')
    reader=csv.reader(infile)        
    outfile=open(outfileName,'wb')
    writer=csv.writer(outfile)
    rowCount = 0
    rowsPadded = 0        
    for row in reader:
        if rowCount == 0:
            # header line
            # find the number of columns in header row numbers of the specified fields
            nColsHeader = len(row)
            print infileName+" has "+str(nColsHeader)+" cols in the header"
        nCols = len(row)
        if (nCols < nColsHeader):
            rowsPadded += 1
            while (nCols < nColsHeader):
                row.append("")
                nCols += 1
        writer.writerow(row)
        rowCount += 1
    print "infile: ",infileName
    print "finished padding ",rowsPadded," rows."
    print "outfile: ",outfileName

# firstRow is the first data row number to display. 
#  if firstRow==1, it will display the first line of data 
# lastRow is the final row number to display.
# if outfileName = None, then it not write to outfile 
def shorten_file(self,infileName,hasHeader,firstRow,lastRow):
    tokens = infileName.split(".")
    outfileName = tokens[0]+"_short."+tokens[1]
    print "creating a shortened version of",infileName
    print " from row",firstRow,"to row",lastRow
    print " to file",outfileName
    infile=open(infileName,'rb')
    reader=csv.reader(infile)
    outfile=open(outfileName,'wb')
    writer=csv.writer(outfile)
    rowCount=-1
    if not hasHeader:
        rowCount += 1
    for row in reader:
        rowCount += 1
        if rowCount == 0:
            # header line
            header = row
            writer.writerow(header)
        if firstRow <= rowCount and rowCount <= lastRow:
            writer.writerow(row)
        if rowCount > lastRow:
            break
    infile.close()
    outfile.close()


class Tally:
    def __init__(self):
        self.freq={}
    def initialize(self,key):
        self.freq[key] = 0
    def add(self,key):
        if self.freq.has_key(key):
            thisFreq = int(self.freq[key])
            thisFreq += 1
            self.freq[key] = thisFreq
        else:
            self.freq[key] = 1
    def getKeys(self):        
        keysList = self.freq.keys() 
        keysList.sort()
        return keysList
    def getVal(self,key):
        return self.freq[key]
    def getFreq(self,key):
        rv = 0
        if self.freq.has_key(key):
            rv = self.freq[key]
        return rv
    def getTot(self):
        tot = 0
        keys = self.freq.keys()
        for key in keys:
            tot += self.getFreq(key)
        return tot
    def showAll(self):
        for key in self.freq:
            print key,self.freq[key]
    def getVals(self):
        return self.freq.values()

def colVals(self,infileName,fieldName):
    print "getting distribution of values for",fieldName,"in file",infileName
    tally = {}
    infile=open(infileName,'rb')
    reader=csv.reader(infile)
    rowCounter = -1
    col = -1
    for row in reader:
        rowCounter += 1
        if rowCounter == 0:
            # find col
            colCounter = 0
            for token in row:
                if token==fieldName:
                    col = colCounter
                colCounter += 1
        else:
            if col == -1:
                print "Error: field value",fieldName,"not found."
                sys.exit(0)

            ### temp -- remove later    
            if rowCounter % 1000000 == 0:
                print fieldName,": row",rowCounter,"is",row
            ###  -   ----- end remove later
                
            fv = row[col]
            if tally.has_key(fv):
                thisFreq = tally[fv]
                thisFreq += 1
                tally[fv] = thisFreq
            else:
                tally[fv] = 1
    tItems = tally.items()
    #tItems = sorted(tItems, key=lambda element: element[1])
    tItems = sorted(tItems, key=lambda element: element[0])
    #tItems.reverse()
    print "value,count,%"
    for tItem in tItems:
        fv = tItem[0]
        count = tItem[1]
        pct = 100.0*count/rowCounter
        print fv,",",count,",%","%.2f" %pct
    print "total",rowCounter
    print "total item values",len(tItems)
    tKeys = tally.keys()
    return tKeys

# check if station ids are unique even across different roads
def xmlStationIdDistr(self,url):
    freq = {}
    dom = minidom.parse(urllib.urlopen(url))
    stations = []
    for node in dom.getElementsByTagName('station'):
        stations.append(node.getAttribute('id'))
    for station in stations:
        if freq.has_key(station):
            thisFreq = freq[station]
            thisFreq += 1
            print "station "+station+" now has "+str(thisFreq)+" count"
            freq[station] = thisFreq
        else:
            freq[station] = 1
    stationList = []
    for station in freq:
        stationList.append(station)
    stationList.sort(key=int)
    for station in stationList:
        print station,'has freq: ',freq[station]

# For the NOVA 5min station dataset, this 
#  returns a dictionary stationID => (lat,lon)
# This was used for the artifact 
#  "Northern Virginia (NOVA) 5-minute Detector Station Data"
#  for which the station coordinates were in a separate xml file.
def xmlReadStationConfig(infile):
    from xml.dom import minidom
    stationLatLongs = {}
    #dom = minidom.parse(urllib.urlopen(url))
    dom = minidom.parse(infile)
    for node in dom.getElementsByTagName('station'):
        stationId = node.getAttribute('id')
        lat = node.getAttribute('latitude')
        lon = node.getAttribute('longitude')
        coord = (lat,lon)
        stationLatLongs[stationId]=coord
    return stationLatLongs

# This was used for the artifact 
#  "Northern Virginia (NOVA) 5-minute Detector Station Data"
#  for which the station coordinates were in a separate xml file.
def createStationConfigFromXml():
    stationLatLongs = xmlReadStationConfig("D:/Nathan L13a/Data/L02/NOVA/NOVA 5min station data set/original data/nova-eqset.xml")
    outfileName = "D:/Nathan L13a/Data/L02/NOVA/NOVA 5min station data set/archived 20130522/nova_station_configs.csv"
    outfile = open(outfileName,'wb')
    writer = csv.writer(outfile)
    header = ["Station ID","Latitude","Longitude"]
    writer.writerow(header)
    artifactStationList = stationLatLongs.keys()
    artifactStationList.sort(key = int)
    for station in artifactStationList:
        coord = stationLatLongs[station]
        lat = coord[0]
        lon = coord[1]
        row = [station,lat,lon]
        writer.writerow(row)
    outfile.close()

# line numbering starts at 1
def grep(file,searchString,lineNumbering):
    print "searching for",searchString,"in",file
    infile = open(file,'rb')
    lineCount = 0
    for line in infile:
        lineCount += 1
        if searchString in line:
            if lineNumbering:
                print lineCount,line
            else:
                print line
    infile.close()
       
def round_n_dec(x,ndec):
    fmt = "%."+str(ndec)+"f"
    return fmt%x

class PdfBin:
    def __init__(self,minval,dx):
        self.minval = minval
        self.maxval = self.minval + dx
    def increment30s(self,dx):
        self.minval += dx
        self.maxval += dx
    def isInside(self,range_,ndec):
        epsilon = 2*10**(-ndec)
        return (self.maxval - range_.maxval < epsilon \
                and range_.minval - self.minval < epsilon)
    def contains(self,x):
        return self.minval <= x and x < self.maxval
    def getMid(self,ndec):
        mid = 0.5*(self.minval+self.maxval)
        midf = round_n_dec(mid,ndec)
        return midf
    @staticmethod
    def find_bin_mid_f(x,all_bins,ndec):
        xmidf = None
        for b in all_bins:
            if b.contains(x):
                xmidf = b.getMid(ndec)
        return xmidf    
    
class PdfRange:
    def __init__(self,minval,maxval):
        self.minval = minval
        self.maxval = maxval

def find_all_bins(dx,r,ndec):
    bins = []
    b = PdfBin(r.minval,dx)
    while b.isInside(r,ndec):
        bins.append(copy.deepcopy(b))
        b.increment30s(dx)
    return bins

def pdf(a,dx,xmin,xmax,ndec,title,xlabel):
    # initialize bins count
    import Plot as plot
    r = PdfRange(xmin,xmax) 
    freq = {}
    all_bins = find_all_bins(dx,r,ndec)
    for b in all_bins:
        freq[b.getMid(ndec)] = 0
    # count freqs
    maxFreq = 0
    for x in a:
        xmidf = PdfBin.find_bin_mid_f(x,all_bins,ndec)
        if xmidf != None:
            freq[xmidf] += 1
            maxFreq = max(maxFreq,freq[xmidf])
    # report function
    xvals = []
    yvals = []
    for b in find_all_bins(dx,r,ndec):
        xmidf = b.getMid(ndec)
        xmid = float(xmidf)
        xvals.append(xmid)
        yvals.append(freq[xmidf])
    plot.ScatterPlot.newPlot(title,xlabel,"freq")
    plot.ScatterPlot.set_axis_ranges(xmin,xmax,0,maxFreq)
    plot.ScatterPlot.addSeries(xvals, yvals,"-","Freq")
    #outfile = io.outpath + str(loopInt)+"_"+str(targetTime_h)+"r"+str(timeRange_s)+"s.png"
    #plot.ScatterPlot.print_to_file(outfile)
    plot.ScatterPlot.show()
    #sp.clear()
    
def pdf_two_series(a1,a2,dx,xmin,xmax,ndec,title,xlabel,series1name,series2name,outfile):
    # initialize bins count
    import Plot as plot
    r = PdfRange(xmin,xmax) 
    freq1 = {}
    freq2 = {}
    all_bins = find_all_bins(dx,r,ndec)
    for b in all_bins:
        freq1[b.getMid(ndec)] = 0
        freq2[b.getMid(ndec)] = 0
    # count freqs
    maxFreq = 0
    for x in a1:
        xmidf = PdfBin.find_bin_mid_f(x,all_bins,ndec)
        if xmidf != None:
            freq1[xmidf] += 1
            maxFreq = max(maxFreq,freq1[xmidf])
    for x in a2:
        xmidf = PdfBin.find_bin_mid_f(x,all_bins,ndec)
        if xmidf != None:
            freq2[xmidf] += 1
            maxFreq = max(maxFreq,freq2[xmidf])        
    # report functions
    xvals = []
    y1vals = []
    y2vals = []
    for b in find_all_bins(dx,r,ndec):
        xmidf = b.getMid(ndec)
        xmid = float(xmidf)
        xvals.append(xmid)
        y1vals.append(freq1[xmidf])
        y2vals.append(freq2[xmidf])
    plot.ScatterPlot.newPlot(title,xlabel,"freq")
    plot.ScatterPlot.set_axis_ranges(xmin,xmax,0,maxFreq)
    plot.ScatterPlot.addSeries(xvals, y1vals,"--",series1name)
    plot.ScatterPlot.addSeries(xvals, y2vals,"-",series2name)
    plot.ScatterPlot.addLegend(1)
    plot.ScatterPlot.print_to_file(outfile)
    plot.ScatterPlot.show()
    #sp.clear()

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def findBlankLines(infileName):
    infile = open(infileName,'rb')
    blanks = []
    lineCount = 0
    for line in infile:
        lineCount += 1
        if line.strip() == "":
            blanks.append(lineCount)
    for blank in blanks:
        print blank        
        
class ScatterPlot:
    @staticmethod
    def newPlot(title,xlabel,ylabel):
        plot.title(title)
        plot.xlabel(xlabel)
        plot.ylabel(ylabel)
    @staticmethod
    def addSeries(xvals,yvals,symbol,label):
        plot.plot(xvals,yvals,symbol,label=label)
    @staticmethod
    def addLegend(loc=3):
        plot.legend(loc=loc)
    @staticmethod
    def set_axis_ranges(xmin,xmax,ymin,ymax):
        plot.axis([xmin,xmax,ymin,ymax])
    @staticmethod
    def show():
        plot.show()
    @staticmethod
    def print_to_file(outfileName):
        plot.savefig(outfileName)
        print "figure printed to",outfileName
    @staticmethod
    def plot_sup():
        plot.plot([1,2,3,4], [1,4,9,16], 'ro')
        plot.plot([1,2,3,4], [2,2,3,3],'r--')
        plot.ylabel('ylabel')
        plot.axis([0, 6, 0, 20])
        plot.show()
    @staticmethod
    def clear():
        plot.clf()        

class DataFrame:
    def __init__(self):
        self.header = []
        self.rows = []
    def setHeader(self,header):
        self.header = header
    def setRows(self,rows):
        self.rows = rows
    def addList(self,listName,listElements):
        #adds to a blank data frame only
        self.header.append(listName)
        for element in listElements:
            row = {}
            row[listName] = element
            self.rows.append(row)            
    @staticmethod
    def read_csv(infileName,header=None):
        # if header is supplied, it is used instead
        # if header=None, then the header is read as the first line of the csv file
        rows = []
        infile = open(infileName,'rb')
        reader = csv.reader(infile)
        if header == None:
            header = next(reader)
        for row in reader:
            d = {}
            for i in range(len(header)):
                field = header[i]
                d[field] = row[i]
            rows.append(d)
        infile.close()
        df = DataFrame()
        df.setHeader(header)
        df.setRows(rows)
        return df
    def write_csv(self,outfileName):
        outfile = open(outfileName,'wb')
        writer = csv.writer(outfile)
        writer.writerow(self.header)
        for row in self.rows:
            outrow = []
            for field in self.header:
                outrow.append(row[field])
            writer.writerow(outrow)
        outfile.close()
    def sortAscendingNumericBy(self,field):
        self.rows.sort(key = lambda x: float(x[field]))
    @staticmethod
    def read_as_list(infileName,hasHeader = False):
        m = []
        infile = open(infileName,'rb')
        reader = csv.reader(infile)
        if hasHeader:
            header = next(reader)
        for row in reader:
            m.append(row[0])
        infile.close()
        return m
    @staticmethod
    def insertHeader(infileName,outfileName,header):
        outfile = open(outfileName,'wb')
        writer = csv.writer(outfile)
        writer.writerow(header)
        infile = open(infileName,'rb')
        reader = csv.reader(infile)
        for row in reader:
            writer.writerow(row)
        outfile.close()
        infile.close()
#     def cbind(self,df):
#         # binds columns in another data frame on to this one
#         # todo: similar to DataSeries.toExcelPlot
#         print ""
    def filter(self,field,value,type="string"):
        newRows = []
        for row in self.rows:
            if type == "string":
                if row[field] == value:
                    newRows.append(row)
            if type == "int":
                if int(row[field]) == value:
                    newRows.append(row)
            if type == "float":
                if float(row[field]) == value:
                    newRows.append(row)
        self.rows = newRows
    def extractColumn(self,field,type="string"):
        outlist = []
        for row in self.rows:
            if type == "string":
                outlist.append(row[field])
            if type == "int": 
                outlist.append(int(row[field]))
            if type == "float":
                outlist.append(float(row[field]))
        return outlist
    @staticmethod
    def listMultiply(thisList,factor):
        newList = []
        for element in thisList:
             newList.append(element*factor)
        return newList
        