import ROOT as r
import h5py
import glob
import os
import optparse
import shutil
import numpy as np

parser = optparse.OptionParser()
parser.add_option("-d", "--dir", dest="directory", default=".")
parser.add_option("-t", "--template", dest="template", default="sigTemplateMakerWithInterpolation")
parser.add_option("-m","--masspoint", dest="masspoint", type=int, default=-1, help="starting mass for scan")
parser.add_option("-l","--binMin", dest="binMin", type=float, default=1600., help="lower boundary of bins")
parser.add_option("-u","--binMax", dest="binMax", type=float, default=6500., help="upper boundary of bins")

(options, args) = parser.parse_args()

#directory = "sigTrainQstar2000_W400_UL17-and-Wp3000_B400_UL17-and-XYY_X3000_Y80_UL17_bkgTrainQCDBKG_mjjFlat_mjj800_ptCut300_INJECT_XYY_X3000_Y80_UL17_XS_10fb_35BkgFiles_10percConsidered_9Bins_sigTemplateMakerWithInterpolation_XToYYprimeTo4Q_MY80_MYprime170"
#masspoint = 3000

directory = options.directory
template = options.template
masspoint = options.masspoint

binMin = options.binMin
binMax = options.binMax

BinList = glob.glob(directory+"/*.h5")

for bl in range(len(BinList)):
    BinList[bl] = BinList[bl].split("/")[-1]
    BinList[bl] = BinList[bl].split(".")[0]

BinList.sort()
BinList.sort(key=lambda val: int(val.split("_")[4]))
#print(BinList)


BinList2d = []

for b in range(len(BinList)):
    newColumn = True
    columnVal = 0
    if(not len(BinList2d) == 0):
        for bc2 in range(len(BinList2d)):
            if(not len(BinList2d[bc2]) == 0):
                if( int(BinList[b].split("_")[1]) == int(BinList2d[bc2][0].split("_")[1]) ):
                    newColumn = False
                    columnVal = bc2
                    break
                elif( int(BinList[b].split("_")[1]) < int(BinList2d[bc2][0].split("_")[1]) ):
                    columnVal = bc2
                    newColumn =False
                    BinList2d.insert(bc2, [])
                    break
    if(newColumn):
        columnVal = len(BinList2d)
        BinList2d.append([])

    #print(columnVal)
    appended = False
    for b3 in range(len(BinList2d[columnVal])):
        if(not len(BinList2d[columnVal]) == 0):
            if( int(BinList[b].split("_")[4]) < int(BinList2d[columnVal][b3].split("_")[4]) ):
                BinList2d[columnVal].insert(b3, BinList[b])
                appended=True
    if(not appended):
        BinList2d[columnVal].append(BinList[b])

#print('\n \n')
#print(BinList2d)


#signalRate = r.TH2F( 'signalRate', 'Signal Fraction in Bin', 9, 0, 9, 9, 0, 9 )
#binnedSignificances = r.TH2F( 'binnedSignificances', 'Per-bin significance from individual fit', 9, 0, 9, 9, 0, 9 )

expectedSignal = []
foundSignal = []
for i in range(9):
    expectedSignal.append([0 for i in range(9)])
    foundSignal.append([0 for i in range(9)])


templateTop = os.getcwd()

os.chdir(directory)

dc_file = open("combineCommandv2.sh","w")
dc_file.write('combineCards.py ')
dc_file.close()

#print('BinList2d')
#print(BinList2d)

for b1 in range(len(BinList2d)):
    #print('hello, here is a b1: ', b1, ' what is BinList2d? ', BinList2d)
#for b1 in range(1):
    for b2 in range(len(BinList2d[b1])):
        #print('hello, here is a b1: ', b2, ' BinList2d[b1] is ', BinList2d[b1])
        #print(b1, BinList2d[b1])
        #print(b2, BinList2d[b1][b2])
        #print(BinList2d[-1-b1][-1-b2])
        #print(BinList2d[-1-b2][b1])

        if("_10000_sigL_-10000_" in BinList2d[-1-b2][b1]):
            print(BinList2d[-1-b2][b1])
            cmd = "python "+templateTop+"/dijetfit.py -i "+BinList2d[-1-b2][b1]+".h5 -M "+str(masspoint)+" --sig_shape "+templateTop+"/"+template+"/graviton_interpolation_M"+str(masspoint)+".0.root --dcb-model -p plots_M"+str(masspoint)+"_"+BinList2d[-1-b2][b1]+" --printSig True -t "+BinList2d[-1-b2][b1]+" -c True --binMin "+str(binMin)+" --binMax "+str(binMax)+" > /dev/null"
            os.system(cmd)
        else:
            print(BinList2d[-1-b2][b1])
            cmd = "python "+templateTop+"/dijetfit.py -i "+BinList2d[-1-b2][b1]+".h5 -M "+str(masspoint)+" --sig_shape "+templateTop+"/"+template+"/graviton_interpolation_M"+str(masspoint)+".0.root --dcb-model -p plots_M"+str(masspoint)+"_"+BinList2d[-1-b2][b1]+" --printSig True -t "+BinList2d[-1-b2][b1]+" --binMin "+str(binMin)+" --binMax "+str(binMax)+" > /dev/null"
            os.system(cmd)

        cmd2 = "combine -M MultiDimFit datacard_JJ_"+BinList2d[-1-b2][b1]+"_FLOAT.txt -m "+str(masspoint)+" -P r -n fit_test_single > /dev/null"
        os.system(cmd2)
        f_signif = r.TFile.Open("higgsCombinefit_test_single.MultiDimFit.mH"+str(masspoint)+".root", "READ")
        res1 = f_signif.Get("limit")
        try:
            res1.GetEntry(0)
            signif = res1.r
        except:
            signif = -1.
        #print('SIGNAL = '+str(signif*100.))
        foundSignal[-1-b2][b1] = signif*100.
            

        #f = h5py.File(BinList2d[b1][b2]+'.h5', 'r')
        #signalRate.SetBinContent(b1+1,b2+1,f['fracSig'][0])
        f = h5py.File(BinList2d[-1-b2][b1]+'.h5', 'r')
        expectedSignal[-1-b2][b1] = f['fracSig'][0]

        

    numHigh = 0
    for b2 in range(len(BinList2d[b1])):
        if(foundSignal[-1-b2][b1] > 1.):
            numHigh += 1

    if(b1==0):
        dc_file = open("combineCommandv2.sh","a")
        for b2 in range(len(BinList2d[b1])):
            dc_file.write('bin_'+BinList2d[-1-b2][b1]+'=datacard_JJ_'+BinList2d[-1-b2][b1]+'.txt ')
        dc_file.close()
    
    else:
        dc_file = open("combineCommandv2.sh","a")
        for b2 in range(len(BinList2d[b1])):
            dc_file.write('bin_'+BinList2d[-1-b2][b1]+'=datacard_JJ_'+BinList2d[-1-b2][b1]+'.txt ')
        dc_file.close()

        print('NUMHIGH = ', numHigh)
        if(numHigh < 5):
            break

dc_file = open("combineCommandv2.sh","a")
dc_file.write('> fullCard.txt')
dc_file.close()

os.system("source ./combineCommandv2.sh")
os.system("text2workspace.py fullCard.txt")
#os.system("timeout 10m combine -M Significance fullCard.root -m "+str(masspoint)+" -n significance_COMBO_PLC_"+str(binMin)+"_"+str(binMax)+" --usePLC")
os.system("timeout 10m combine -M Significance fullCard.root -m "+str(masspoint)+" -n significance_COMBO_"+str(binMin)+"_"+str(binMax))
os.system("timeout 10m combine -M AsymptoticLimits fullCard.root -m "+str(masspoint)+" -n lim_"+str(binMin)+"_"+str(binMax))


signalTotals = open("signalTotals_M"+str(int(masspoint))+"_range_"+str(binMin)+"_"+str(binMax)+".txt","r")
sTLines = signalTotals.readlines()
numberQUAKBINs = 0
totalSignal_ExpectedInBins = 0.
for stline in sTLines:
    numberQUAKBINs += 1
    totalSignal_ExpectedInBins += float(stline)
signalTotals.close()

binsChecked = 0
signalFractionConsidered = 0.
for b1 in range(len(BinList2d)):
    for b2 in range(len(BinList2d[b1])):
        if(binsChecked < numberQUAKBINs):
            with h5py.File(BinList2d[-1-b2][b1]+".h5", "r") as f:
                signalFractionConsidered += np.array(f['fracSig'][0])
            binsChecked+=1
        

print("totalSignal_ExpectedInBins = ", totalSignal_ExpectedInBins)
print("signalFractionConsidered = ", signalFractionConsidered)

signalNorm = totalSignal_ExpectedInBins/signalFractionConsidered

print("signalNorm", signalNorm)


#higgsCombinelim_1800.0_3400.0.AsymptoticLimits.mH2600.root
f_limit_name = 'higgsCombinelim_'+str(binMin)+'_'+str(binMax)+'.AsymptoticLimits.mH'+str(masspoint)+'.root'
f_limit = r.TFile(f_limit_name, "READ")
res2 = f_limit.Get("limit")
eps = 0.01
obs_limit = -1
exp_limit = exp_low = exp_high = exp_two_low = exp_two_high = -1

for i in range(6):
    res2.GetEntry(i)
    if(res2.quantileExpected == -1):  # obs limit
        obs_limit = res2.limit
    elif(abs(res2.quantileExpected - 0.5) < eps):  # exp limit
        exp_limit = res2.limit
    elif(abs(res2.quantileExpected - 0.025) < eps):  # 2sigma, low
        exp_two_low = res2.limit
    elif(abs(res2.quantileExpected - 0.16) < eps):  # 1sigma, low
        exp_low = res2.limit
    elif(abs(res2.quantileExpected - 0.84) < eps):  # 1sigma, high
        exp_high = res2.limit
    elif(abs(res2.quantileExpected - 0.975) < eps):  # 2sigma, high
        exp_two_high = res2.limit
        
print("Obs limit is %.3f (%.1f events)" % (obs_limit, obs_limit*signalNorm))
print("Expected was %.3f (%.1f events)" % (exp_limit, exp_limit*signalNorm))
print("Expected range %.1f-%.1f (one sigma), %.1f-%.1f (two sigma)" % (exp_low * signalNorm, exp_high*signalNorm, exp_two_low * signalNorm, exp_two_high * signalNorm))

limitInfo = open("limitInfo_M"+str(masspoint)+"_range_"+str(binMin)+"_"+str(binMax)+".txt","a")
limitInfo.write('totalSignal_ExpectedInBins = '+str(totalSignal_ExpectedInBins)+'\n')
limitInfo.write('signalFractionConsidered = '+str(signalFractionConsidered)+'\n')
limitInfo.write('signalNorm = '+str(signalNorm)+'\n')
limitInfo.write("Obs limit is %.3f (%.1f events)" % (obs_limit, obs_limit*signalNorm)+'\n')
limitInfo.write("Expected was %.3f (%.1f events)" % (exp_limit, exp_limit*signalNorm)+'\n')
limitInfo.write("Expected range %.1f-%.1f (one sigma), %.1f-%.1f (two sigma)" % (exp_low * signalNorm, exp_high*signalNorm, exp_two_low * signalNorm, exp_two_high * signalNorm)+'\n')
limitInfo.close()

os.chdir(templateTop)

print(expectedSignal)
print(foundSignal)

