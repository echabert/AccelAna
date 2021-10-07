import statistics as stat
import matplotlib.pyplot as plt

cvsFilename = "peaks.csv"

################################################################
# For a given array (accel in a given coordinate), find the peaks
################################################################

def PeakFinder(val,time,dump=False, twindow=3):
    if dump:
        print("#measures:",len(val))
        print("mean: ",stat.mean(val))
        print("median:",stat.median(val))
    median = stat.median(val)
    
    #compute rms w/o signal
    stdev = stat.pstdev([i for i in val if i<median])
    if dump:
        print("stdev:",stdev)
    
    #suppress all data below a threhod: median+3*stdev
    valzs = [i if i>(median+2*stdev) else 0 for i in val]
    
    #look for time inside a window of twindow seconds
    shocks = []
    #out=[]
    nl = []
    first=True
    tref = 0
    for v,t in zip(valzs[:],time[:]):
        if (v>0 and first) or (len(nl)>0 and abs(t-tref)<twindow and t!=tref):
            #out.append(v)
            nl.append(v)
            if first: 
                first=False
                tref=t
        elif nl:
            first=True
            shocks.append(nl[:])
            nl.clear()
        #out.append(0)
    

    #print(shocks)
    #print([len(i) for i in shocks])
    #print([max(i)  for i in shocks if len(i)>12])
    maxshocks=[max(i)  for i in shocks if len(i)>12]
    """
    out2=[0]*len(val)
    for m in maxshocks:
        out2[val.index(m)]=m
    return out,out2,maxshocks
    """
    
    return maxshocks




################################################################
# Return arrays of x,y,z,t for a give probe
################################################################
def GetData(filename,probename="mt1"):
    xval = []
    yval = []
    zval = []
    tval = []
    with open(filename) as f:
        counter=0
        for line in f:
            #ignore the first lines (header)
            counter+=1
            if counter<5: continue
            #print(line)
            
            if len(line.split(','))<10: continue
            val = float(line.split(',')[6])
            #time: min*60+sec
            time = float(line.split(',')[5].split(':')[-2])*60+float(line.split(',')[5].split(':')[-1].replace("Z",''))
            axis = line.split(',')[7]
            probe = line.split(',')[9].split()[0]
            
            if probe==probename:
                if axis=="x-axis": xval.append(val)
                if axis=="y-axis": yval.append(val)
                if axis=="z-axis": zval.append(val)
            tval.append(time)
    return xval,yval,zval,tval

def DoPlot(rawval,maxshocks):
    #produce a new array with 0 when there was no peaks
    zsVal=[0]*len(rawval)
    for m in maxshocks:
        zsVal[rawval.index(m)]=m
    plt.plot(rawval,label="raw")
    plt.plot(zsVal,label="peaks")
    plt.legend()



def FileAna(filename):
    print("###############################")
    print("Analysis of file:",filename)

    probes=["mt1","mt2","mt3","mt4"]
    axisLabels=["x","y","z"]
    report=""
    report+="filename: "+filename+"\n"
    cvsFormat=""

    results={p:{} for p in probes}

    for probe in probes:
        x,y,z,t = GetData(filename,probe)
        axes={"x":x,"y":y,"z":z}
        results[probe]={a:{} for a in axes}
        for a,val in axes.items():
            maxshocks = PeakFinder(val,t)
            #DoPlot(val,maxshocks)
            #print(stat.mean(maxshocks),stat.stdev(maxshocks))
            report+=f"probe: {probe}\t{a}-axis: {stat.mean(maxshocks)} \t +/- {stat.pstdev(maxshocks)/len(maxshocks)} \t nshocks: {len(maxshocks)}\n"
            results[probe][a]["mean"] = stat.mean(maxshocks)
            results[probe][a]["meanErr"] = stat.pstdev(maxshocks)/len(maxshocks)
            results[probe][a]["stdev"] = stat.stdev(maxshocks)
            results[probe][a]["nshocks"] = len(maxshocks)

    for p in probes:
        for a in axisLabels:
            cvsFormat+="{:.4f}".format(results[p][a]["mean"])
            cvsFormat+=","
            cvsFormat+="{:.4f}".format(results[p][a]["meanErr"])
            cvsFormat+=","

    cvsFormat+="\n"
    print(report)
    print(results)
    with open(cvsFilename,"a") as ofile:
        ofile.write(cvsFormat)
    
    print("###############################")

#filename="test1-4sensor-60s-800Hz.csv"
#filename="mt4-4choc-fort_csv.csv"
#filename="data/mt-fermee-module-sans-mousse-X-1.csv"


#remove csv file
import os
if os.path.exists(cvsFilename):
    os.remove(cvsFilename)

filenames=["data/mt-ouverte-vide-X-{}.csv".format(i) for i in range(1,4)] 
filenames+=["data/mt-fermee-vide-X-{}.csv".format(i) for i in range(1,4)] 
filenames+=["data/mt-fermee-pleine-X-{}.csv".format(i) for i in range(1,4)] 
print(filenames)

for f in filenames:
    FileAna(f)

