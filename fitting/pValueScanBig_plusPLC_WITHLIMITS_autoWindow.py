#!/usr/bin/env python                                                                                                                                                                                                       
import ROOT as r,sys,math,array,os
from optparse import OptionParser
from ROOT import std,RooDataHist
from array import array
import numpy as np
#from scipy.stats import poisson, norm, kstest, chi2
from scipy import stats
import sys

#resMass = 1900
#nominal = True


def end():
    if __name__ == '__main__':
        rep = ''
        while not rep in [ 'q', 'Q','a',' ' ]:
            rep = input( 'enter "q" to quit: ' )
            if 1 < len(rep):
                rep = rep[0]


if __name__ == "__main__":
    r.gROOT.SetBatch(r.kTRUE)

    #sigTrainQstar2000_W400_UL17-and-Wp3000_B400_UL17-and-XYY_X3000_Y80_UL17_bkgTrainQCDBKG_INJECT_XYY_X3000_Y80_UL17_XS_100fb_15BkgFiles_10percConsidered_5Bins_sigTemplateMakerWithInterpolation_QstarToQW_mW_400

    #sigTrains = ['sigTrainQstar2000_W400_UL17-and-Wp3000_B400_UL17-and-XYY_X3000_Y80_UL17_bkgTrainQCDBKG', 'sigTrainWp3000_B400_UL17-and-XYY_X3000_Y80_UL17_bkgTrainQCDBKG', 'sigTrainQstar2000_W400_UL17-and-Wp3000_B400_UL17-and-XYY_X3000_Y80_UL17_bkgTrainQCDBKG', 'sigTrainXYY_X3000_Y80_UL17_bkgTrainQCDBKG', 'sigTrainWp3000_B400_UL17_bkgTrainQCDBKG']
    #sigTrains = ['sigTrainQstar2000_W400_UL17-and-Wp3000_B400_UL17-and-XYY_X3000_Y80_UL17_bkgTrainQCDBKG', 'sigTrainWp3000_B400_UL17-and-XYY_X3000_Y80_UL17_bkgTrainQCDBKG', 'sigTrainXYY_X3000_Y80_UL17_bkgTrainQCDBKG', 'sigTrainWp3000_B400_UL17_bkgTrainQCDBKG', 'sigTrainWp5000_B400_UL17_bkgTrainQCDBKG']
    #sigTrains = ['sigTrainQstar2000_W400_UL17-and-Wp3000_B400_UL17-and-XYY_X3000_Y80_UL17_bkgTrainQCDBKG_mjjFlat_mjj800_ptCut300', 'sigTrainWp3000_B400_UL17-and-XYY_X3000_Y80_UL17_bkgTrainQCDBKG_mjjFlat_mjj800_ptCut300', 'sigTrainXYY_X3000_Y80_UL17_bkgTrainQCDBKG_mjjFlat_mjj800_ptCut300', 'sigTrainWp3000_B400_UL17_bkgTrainQCDBKG_mjjFlat_mjj800_ptCut300', 'sigTrainQstar2000_W400_UL17_bkgTrainQCDBKG_mjjFlat_mjj800_ptCut300']
    sigTrains = ['sigTrainQstar2000_W400_UL17-and-Wp3000_B400_UL17-and-XYY_X3000_Y80_UL17_bkgTrainQCDBKG_mjjFlat_mjj800_ptCut300']
    sigInjects = ['XYY_X3000_Y80_UL17', 'Wp3000_B400_UL17']
    #sigInjects = ['Wp3000_B400_UL17', 'XYY_X3000_Y80_UL17', 'Qstar2000_W400_UL17']
    XSs = ['1', '10', '30', '100']
    sigTemplates = ['sigTemplateMakerWithInterpolation_XToYYprimeTo4Q_MY80_MYprime170', 'sigTemplateMakerWithInterpolation_WpToBpT_Bp400_Top170', 'sigTemplateMakerWithInterpolation_QstarToQW_mW_400', 'sigTemplateMakerWithInterpolation']
    Ms = range(1700,6000,100)

    binNum = '9Bins_'

    sliceName = "testAllSlices"
    #extraNameString = '_includeBF'
    extraNameString = ''
    
    #dateName = 'Oct06'
    #dateName = 'Oct12'
    dateName = 'Oct12_pullGeneral'


    rMaxTest = False
    rMaxes = ['_0.5', '_1', '_5', '_10']

    if(rMaxTest):
        myFile = r.TFile.Open("pValusScanBIG_"+sliceName+extraNameString+"_rMaxTest.root", "UPDATE")
    else:
        myFile = r.TFile.Open("pValusScanBIG_"+sliceName+extraNameString+"_"+dateName+"_autoWindow_WITHLIMITS.root", "UPDATE")
    graphs = []
    graphs2 = []
    graphs3 = []
    graphs4 = []

    graphsObs = []
    graphsExp = []
    graphsExpRangeLow = []
    graphsExpRangeHigh = []
    graphsExpRange2Low = []
    graphsExpRange2High = []

    for sTr in sigTrains:
        for sI in sigInjects:
            for x in XSs:
                for sTe in sigTemplates:
                    xsvals, sigvals, sigvals2, sigvals4, obslimit, explimit, exprangelow, exprangehigh, exprange2low, exprange2high = array( 'd' ), array( 'd' ), array( 'd' ), array( 'd' ), array( 'd' ), array( 'd' ), array( 'd' ), array( 'd' ), array( 'd' ), array( 'd' )
                    sigvals3 = []
                    if(rMaxTest):
                        for rmt in range(len(rMaxes)):
                            sigvals3.append(array( 'd' ))
                    n=0
                    #for entry in myTree:
                    for m in Ms:

                        #${m}-$((800+25*(${m}-2200)/100)
                        windowsize = (800 + 25 * (m-2200)/100)
                        window = [-1*(windowsize), windowsize]
                        
                        #f_signif_name = sTr+'_INJECT_'+sI+'_XS_'+x+'fb_15BkgFiles_10percConsidered_5Bins_'+sTe+'/higgsCombinesignificance_COMBO.Significance.mH'+str(m)+'.root'
                        f_signif_name = sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe+'/higgsCombinesignificance_COMBO_'+str(m+window[0])+".0_"+str(m+window[1])+'.0.Significance.mH'+str(m)+'.root'
                        f_signif_name_plc = sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe+'/higgsCombinesignificance_COMBO_PLC_'+str(m+window[0])+".0_"+str(m+window[1])+'.0.Significance.mH'+str(m)+'.root'
                        f_limit_name = sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe+'/higgsCombinelim_'+str(m+window[0])+".0_"+str(m+window[1])+'.0.AsymptoticLimits.mH'+str(m)+'.root'
                        #f_signif_name_bf = sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe+'/higgsCombinesignificance_COMBO_BF.Significance.mH'+str(m)+'.root'

                        print(f_signif_name)
                        #print('xrdfs root://cmseos.fnal.gov ls /store/user/wmccorma/CASE_'+dateName+'_'+sliceName+'_WITHLIMITS/'+sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe+'/ | grep higgsCombinesignificance_COMBO_'+str(window[0])+".0_"+str(window[1])+'.0.Significance.mH'+str(m))
                        
                        if(os.system('xrdfs root://cmseos.fnal.gov ls /store/user/wmccorma/CASE_'+dateName+'_'+sliceName+'_WITHLIMITS/'+sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe+'/ | grep higgsCombinesignificance_COMBO_'+str(m+window[0])+".0_"+str(m+window[1])+'.0.Significance.mH'+str(m)) == 256):
                            continue
                        f_signif = r.TFile.Open('root://cmsxrootd.fnal.gov//store/user/wmccorma/CASE_'+dateName+'_'+sliceName+'_WITHLIMITS//'+f_signif_name, "READ")

                        if(os.system('xrdfs root://cmseos.fnal.gov ls /store/user/wmccorma/CASE_'+dateName+'_'+sliceName+'_WITHLIMITS//'+sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe+'/ | grep higgsCombinesignificance_COMBO_PLC_'+str(m+window[0])+".0_"+str(m+window[1])+'.0.Significance.mH'+str(m)) == 256):
                            continue
                        f_signif2 = r.TFile.Open('root://cmsxrootd.fnal.gov//store/user/wmccorma/CASE_'+dateName+'_'+sliceName+'_WITHLIMITS//'+f_signif_name_plc, "READ")


                        if(os.system('xrdfs root://cmseos.fnal.gov ls /store/user/wmccorma/CASE_'+dateName+'_'+sliceName+'_WITHLIMITS//'+sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe+'/ | grep higgsCombinelim_'+str(m+window[0])+".0_"+str(m+window[1])+'.0.AsymptoticLimits.mH'+str(m)) == 256):
                            continue
                        f_limit = r.TFile.Open('root://cmsxrootd.fnal.gov//store/user/wmccorma/CASE_'+dateName+'_'+sliceName+'_WITHLIMITS//'+f_limit_name, "READ")


                        #if(os.system('xrdfs root://cmseos.fnal.gov ls /store/user/wmccorma/CASE_'+dateName+'_'+sliceName+'_WITHLIMITS//'+sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe+'/ | grep signalTotals_M'+str(m)+'_range'+str(m+window[0])+".0_"+str(m+window[1])+'.0.txt') == 256):
                        #    continue
                        #
                        #signalTotals_M5400_range_4200.0_6200.0.txt

                        res1 = f_signif.Get("limit")
                        try:
                            res1.GetEntry(0)
                            signif = res1.limit
                        except:
                            signif = -1.
                        sigvals.append(signif)

                        res2 = f_signif2.Get("limit")
                        try:
                            res2.GetEntry(0)
                            signif2 = res2.limit
                        except:
                            signif2 = -1.
                        sigvals2.append(signif2)


                        #f_limit = ROOT.TFile(f_limit_name, "READ")
                        res3 = f_limit.Get("limit")
                        eps = 0.01
                        obs_limit = -1
                        exp_limit = exp_low = exp_high = exp_two_low = exp_two_high = -1
                        
                        for i in range(6):
                            try:
                                res3.GetEntry(i)
                                if(res3.quantileExpected == -1):  # obs limit
                                    obs_limit = res3.limit
                                elif(abs(res3.quantileExpected - 0.5) < eps):  # exp limit
                                    exp_limit = res3.limit
                                elif(abs(res3.quantileExpected - 0.025) < eps):  # 2sigma, low
                                    exp_two_low = res3.limit
                                elif(abs(res3.quantileExpected - 0.16) < eps):  # 1sigma, low
                                    exp_low = res3.limit
                                elif(abs(res3.quantileExpected - 0.84) < eps):  # 1sigma, high
                                    exp_high = res3.limit
                                elif(abs(res3.quantileExpected - 0.975) < eps):  # 2sigma, high
                                    exp_two_high = res3.limit
                            except:
                                obs_limit = -.0001
                                exp_limit = -.0001
                                exp_two_low = -.0001
                                exp_low = -.0001
                                exp_high = -.0001
                                exp_two_high = -.0001

                        obslimit.append(obs_limit*1680.)
                        explimit.append(exp_limit*1680.)
                        exprangelow.append(exp_low * 1680.)
                        exprangehigh.append(exp_high * 1680.)
                        exprange2low.append(exp_two_low * 1680.)
                        exprange2high.append(exp_two_high * 1680.)

                        xsvals.append(m)
                        n+=1

                    if(n==0):
                        continue
                    graphs.append(r.TGraph(n,xsvals,sigvals))
                    graphs[-1].SetMarkerStyle(20)
                    graphs[-1].GetXaxis().SetTitle("mass [GeV]")
                    graphs[-1].GetYaxis().SetTitle("significance value")
                    graphs[-1].SetTitle(f_signif_name)
                    graphs[-1].Draw("alp")
                    #myFile.WriteObject(graphs[-1], sTr+'_INJECT_'+sI+'_XS_'+x+'fb_15BkgFiles_10percConsidered_5Bins_'+sTe)
                    myFile.WriteObject(graphs[-1], sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe)

                    graphs2.append(r.TGraph(n,xsvals,sigvals2))
                    graphs2[-1].SetMarkerStyle(20)
                    graphs2[-1].GetXaxis().SetTitle("mass [GeV]")
                    graphs2[-1].GetYaxis().SetTitle("significance value (PLC)")
                    graphs2[-1].SetTitle(f_signif_name_plc)
                    graphs2[-1].Draw("alp")
                    myFile.WriteObject(graphs2[-1], sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe+'_PLC')

                    graphsObs.append(r.TGraph(n,xsvals,obslimit))
                    graphsObs[-1].SetMarkerStyle(20)
                    graphsObs[-1].GetXaxis().SetTitle("mass [GeV]")
                    graphsObs[-1].GetYaxis().SetTitle("observed limit [events]")
                    graphsObs[-1].SetTitle(f_limit_name)
                    graphsObs[-1].Draw("alp")
                    myFile.WriteObject(graphsObs[-1], sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe+'_ObsLimit')

                    graphsExp.append(r.TGraph(n,xsvals,explimit))
                    graphsExp[-1].SetMarkerStyle(20)
                    graphsExp[-1].GetXaxis().SetTitle("mass [GeV]")
                    graphsExp[-1].GetYaxis().SetTitle("expected limit [events]")
                    graphsExp[-1].SetTitle(f_limit_name)
                    graphsExp[-1].Draw("alp")
                    myFile.WriteObject(graphsExp[-1], sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe+'_ExpLimit')

                    graphsExpRangeLow.append(r.TGraph(n,xsvals,exprangelow))
                    graphsExpRangeLow[-1].SetMarkerStyle(20)
                    graphsExpRangeLow[-1].GetXaxis().SetTitle("mass [GeV]")
                    graphsExpRangeLow[-1].GetYaxis().SetTitle("expected limit -1 sigma [events]")
                    graphsExpRangeLow[-1].SetTitle(f_limit_name)
                    graphsExpRangeLow[-1].Draw("alp")
                    myFile.WriteObject(graphsExpRangeLow[-1], sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe+'_ExpLimit_-1sigma')

                    graphsExpRangeHigh.append(r.TGraph(n,xsvals,exprangehigh))
                    graphsExpRangeHigh[-1].SetMarkerStyle(20)
                    graphsExpRangeHigh[-1].GetXaxis().SetTitle("mass [GeV]")
                    graphsExpRangeHigh[-1].GetYaxis().SetTitle("expected limit +1 sigma [events]")
                    graphsExpRangeHigh[-1].SetTitle(f_limit_name)
                    graphsExpRangeHigh[-1].Draw("alp")
                    myFile.WriteObject(graphsExpRangeHigh[-1], sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe+'_ExpLimit_+1sigma')

                    graphsExpRange2Low.append(r.TGraph(n,xsvals,exprange2low))
                    graphsExpRange2Low[-1].SetMarkerStyle(20)
                    graphsExpRange2Low[-1].GetXaxis().SetTitle("mass [GeV]")
                    graphsExpRange2Low[-1].GetYaxis().SetTitle("expected limit -2 sigma [events]")
                    graphsExpRange2Low[-1].SetTitle(f_limit_name)
                    graphsExpRange2Low[-1].Draw("alp")
                    myFile.WriteObject(graphsExpRange2Low[-1], sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe+'_ExpLimit_-2sigma')

                    graphsExpRange2High.append(r.TGraph(n,xsvals,exprange2high))
                    graphsExpRange2High[-1].SetMarkerStyle(20)
                    graphsExpRange2High[-1].GetXaxis().SetTitle("mass [GeV]")
                    graphsExpRange2High[-1].GetYaxis().SetTitle("expected limit +2 sigma [events]")
                    graphsExpRange2High[-1].SetTitle(f_limit_name)
                    graphsExpRange2High[-1].Draw("alp")
                    myFile.WriteObject(graphsExpRange2High[-1], sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe+'_ExpLimit_+2sigma')

                    #graphs4.append(r.TGraph(n,xsvals,sigvals4))
                    #graphs4[-1].SetMarkerStyle(20)
                    #graphs4[-1].GetXaxis().SetTitle("mass [GeV]")
                    #graphs4[-1].GetYaxis().SetTitle("significance value (BF)")
                    #graphs4[-1].SetTitle(f_signif_name_bf)
                    #graphs4[-1].Draw("alp")
                    #myFile.WriteObject(graphs4[-1], sTr+'_INJECT_'+sI+'_XS_'+x+'fb_35BkgFiles_10percConsidered_'+binNum+sTe+'_BF')

